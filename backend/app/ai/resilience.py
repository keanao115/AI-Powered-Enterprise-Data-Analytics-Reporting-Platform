import logging
import random
import time
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is OPEN, short-circuiting calls."""

    pass


class CircuitBreaker:
    """
    Production-grade Circuit Breaker pattern for external LLM API providers.
    States:
      - CLOSED: Normal operation. Requests pass through.
      - OPEN: Failures exceeded threshold. Requests are fast-failed or routed to fallback.
      - HALF_OPEN: Trial period after recovery timeout. One request tested.
    """

    def __init__(
        self,
        name: str = "LLMProvider",
        failure_threshold: int = 2,
        recovery_timeout: float = 30.0,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.state: str = "CLOSED"
        self.consecutive_failures: int = 0
        self.last_failure_time: float = 0.0

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            if (now - self.last_failure_time) >= self.recovery_timeout:
                logger.info(
                    f"[{self.name} CircuitBreaker] Recovery timeout elapsed. Transitioning OPEN -> HALF_OPEN."
                )
                self.state = "HALF_OPEN"
                return True
            return False

        if self.state == "HALF_OPEN":
            return True

        return True

    def record_success(self):
        if self.state != "CLOSED":
            logger.info(
                f"[{self.name} CircuitBreaker] Success recorded. Resetting state to CLOSED."
            )
        self.state = "CLOSED"
        self.consecutive_failures = 0

    def record_failure(self, error: Optional[Exception] = None):
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        logger.warning(
            f"[{self.name} CircuitBreaker] Failure #{self.consecutive_failures} recorded. Error: {error}"
        )

        if self.state == "HALF_OPEN" or self.consecutive_failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"[{self.name} CircuitBreaker] Failure threshold ({self.failure_threshold}) reached. Tripping circuit to OPEN."
            )

    def execute_with_fallback(
        self,
        func: Callable[..., Any],
        fallback_func: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        """
        Executes target function protected by circuit breaker.
        If circuit is OPEN or execution fails, seamlessly invokes fallback.
        """
        if not self.can_execute():
            logger.warning(
                f"[{self.name} CircuitBreaker is OPEN] Fast-failing directly to fallback."
            )
            return fallback_func(*args, **kwargs)

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure(e)
            logger.warning(f"[{self.name} Execution Failed] Invoking graceful fallback handler.")
            return fallback_func(*args, **kwargs)


def retry_with_exponential_backoff(
    func: Callable[..., Any],
    max_retries: int = 2,
    base_delay: float = 0.5,
    max_delay: float = 4.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
) -> Any:
    """
    Executes function with exponential backoff and randomized jitter.
    """
    attempt = 0
    while True:
        try:
            return func()
        except retryable_exceptions as exc:
            attempt += 1
            if attempt > max_retries:
                logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}: {exc}")
                raise

            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            if jitter:
                delay = delay * (0.5 + random.random())

            logger.info(
                f"Transient failure in {func.__name__}: {exc}. Retrying in {delay:.2f}s (attempt {attempt}/{max_retries})..."
            )
            time.sleep(delay)
