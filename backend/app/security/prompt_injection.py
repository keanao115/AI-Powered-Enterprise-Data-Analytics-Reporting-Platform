import re
from typing import Tuple


class PromptSecurityScanner:
    """
    Multi-stage Prompt Injection Defense Scanner.
    Detects instruction override attacks, system prompt extraction, credential theft, and system commands.
    """

    PROMPT_INJECTION_PATTERNS = [
        r"ignore (all )?previous instructions",
        r"reveal (the )?system prompt",
        r"disclose (your )?initial instructions",
        r"show (me )?passwords",
        r"dump (all )?tables",
        r"drop table",
        r"delete from",
        r"truncate table",
        r"grant all",
        r"bypass (all )?security",
        r"you are now in developer mode",
        r"dan mode",
    ]

    def scan(self, text: str) -> Tuple[bool, str]:
        if not text:
            return True, "EMPTY"

        clean_text = text.lower()
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, clean_text):
                return False, f"Prompt injection pattern detected: '{pattern}'"

        return True, "SAFE"


prompt_security_scanner = PromptSecurityScanner()
