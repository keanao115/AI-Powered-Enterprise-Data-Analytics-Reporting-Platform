from typing import Any, Dict, List


def evaluate_data_quality(columns: List[str], rows: List[List[Any]]) -> Dict[str, Any]:
    if not rows:
        return {
            "quality_score": 100.0,
            "null_ratio": 0.0,
            "duplicate_count": 0,
            "freshness_status": "FRESH",
            "warnings": ["Empty result set returned"],
        }

    total_cells = len(columns) * len(rows)
    null_cells = 0
    seen_rows = set()
    duplicate_count = 0

    for row in rows:
        row_tuple = tuple(row)
        if row_tuple in seen_rows:
            duplicate_count += 1
        seen_rows.add(row_tuple)

        for val in row:
            if val is None or str(val).strip() in ("", "NULL", "None"):
                null_cells += 1

    null_ratio = round(null_cells / max(total_cells, 1), 4)
    dup_ratio = round(duplicate_count / max(len(rows), 1), 4)

    # Score calculation (100 base)
    score = 100.0 - (null_ratio * 30.0) - (dup_ratio * 20.0)
    score = max(round(score, 1), 0.0)

    warnings = []
    if null_ratio > 0.1:
        warnings.append(f"High null ratio detected: {null_ratio * 100:.1f}% of cells are null")
    if duplicate_count > 0:
        warnings.append(f"Duplicate records found: {duplicate_count} duplicate row(s)")

    return {
        "quality_score": score,
        "null_ratio": null_ratio,
        "duplicate_count": duplicate_count,
        "freshness_status": "UP_TO_DATE",
        "warnings": warnings,
    }
