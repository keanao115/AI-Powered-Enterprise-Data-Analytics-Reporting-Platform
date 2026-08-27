import re
from typing import Any, Dict, List


class DataMaskingEngine:
    """
    Column-level and text-level dynamic data masking engine.
    Masks RESTRICTED / CONFIDENTIAL attributes before presentation or LLM consumption.
    """

    MASKED_COLUMNS = {"ssn", "social_security", "credit_card", "card_number", "password", "secret"}

    def mask_column_name(self, col_name: str) -> bool:
        return col_name.lower() in self.MASKED_COLUMNS

    def mask_value(self, val: Any, col_name: str) -> Any:
        if val is None:
            return None
        col_lower = col_name.lower()
        if col_lower in ("ssn", "social_security"):
            val_str = str(val)
            return "***-**-" + val_str[-4:] if len(val_str) >= 4 else "***-**-****"
        elif col_lower in ("credit_card", "card_number"):
            val_str = str(val)
            return "****-****-****-" + val_str[-4:] if len(val_str) >= 4 else "****-****-****-****"
        elif col_lower in ("email",):
            val_str = str(val)
            parts = val_str.split("@")
            if len(parts) == 2:
                return parts[0][:2] + "***@" + parts[1]
            return "***@***.com"
        elif col_lower in self.MASKED_COLUMNS:
            return "[REDACTED]"
        return val

    def mask_result_set(self, columns: List[str], rows: List[List[Any]]) -> List[List[Any]]:
        masked_rows = []
        for row in rows:
            new_row = []
            for col_name, val in zip(columns, row):
                new_row.append(self.mask_value(val, col_name))
            masked_rows.append(new_row)
        return masked_rows


data_masking_engine = DataMaskingEngine()
