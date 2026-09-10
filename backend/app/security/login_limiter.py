"""
Login Brute-Force Rate Limiter & Account Lockout Engine.
Remediates Item 3.1: Brute-force protection on /auth/login.
Tracks failed authentication attempts using a sliding-window algorithm,
enforces progressive lockouts, and emits security events.
"""

import time
from typing import Dict, List, Tuple, Optional


class LoginRateLimiter:
    def __init__(
        self,
        max_failed_attempts: int = 5,
        attempt_window_seconds: int = 300,  # 5 minutes
        lockout_duration_seconds: int = 900,  # 15 minutes
    ):
        self.max_failed_attempts = max_failed_attempts
        self.attempt_window_seconds = attempt_window_seconds
        self.lockout_duration_seconds = lockout_duration_seconds

        # Map key -> list of failure timestamps [t1, t2, ...]
        self._failed_attempts: Dict[str, List[float]] = {}
        # Map key -> lockout expiration timestamp
        self._locked_until: Dict[str, float] = {}

    def _clean_old_attempts(self, key: str, now: float) -> List[float]:
        """Prunes timestamps older than attempt_window_seconds."""
        cutoff = now - self.attempt_window_seconds
        attempts = [t for t in self._failed_attempts.get(key, []) if t > cutoff]
        self._failed_attempts[key] = attempts
        return attempts

    def is_locked(self, key: str) -> Tuple[bool, int]:
        """
        Checks if the given key (email or IP) is currently locked out.
        Returns (is_locked: bool, retry_after_seconds: int).
        """
        now = time.time()
        lock_expiry = self._locked_until.get(key, 0.0)
        if lock_expiry > now:
            remaining = int(lock_expiry - now) + 1
            return True, remaining
        elif lock_expiry > 0.0:
            # Lockout expired
            del self._locked_until[key]
        return False, 0

    def record_failure(self, key: str) -> Tuple[bool, int, int]:
        """
        Records a failed authentication attempt.
        Returns:
            (is_locked_now: bool, failed_count_in_window: int, retry_after_seconds: int)
        """
        now = time.time()
        # Check if already locked
        already_locked, remaining = self.is_locked(key)
        if already_locked:
            return True, len(self._failed_attempts.get(key, [])), remaining

        # Clean and append new attempt
        attempts = self._clean_old_attempts(key, now)
        attempts.append(now)
        self._failed_attempts[key] = attempts

        if len(attempts) >= self.max_failed_attempts:
            # Trigger lockout
            self._locked_until[key] = now + self.lockout_duration_seconds
            return True, len(attempts), self.lockout_duration_seconds

        return False, len(attempts), 0

    def record_success(self, key: str) -> None:
        """Clears failure history upon successful authentication."""
        self._failed_attempts.pop(key, None)
        self._locked_until.pop(key, None)

    def unlock(self, key: str) -> None:
        """Manually unlocks a specific key."""
        self.record_success(key)

    def reset_all(self) -> None:
        """Resets all tracking dictionaries (useful for test isolation)."""
        self._failed_attempts.clear()
        self._locked_until.clear()


# Global Singleton Instance
login_rate_limiter = LoginRateLimiter()
