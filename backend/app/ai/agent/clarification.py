from typing import Dict, Any, Tuple, List


class AmbiguityDetector:
    """
    Evaluates whether a natural-language business query requires clarification.
    """

    AMBIGUOUS_PATTERNS = {
        "sales": ("metric", ["Revenue (Sum of Completed Order Amount)", "Order Count (Number of Orders)", "Units Sold"]),
        "performance": ("dimension", ["Sales Team Revenue Growth", "Regional Return Rate", "Employee Sales Targets"]),
        "revenue": ("time_period", ["Current Month vs Last Month", "Year-to-Date (YTD)", "Last 30 Days"]),
    }

    def evaluate(self, question: str) -> Tuple[bool, str, List[str]]:
        q_clean = question.strip().lower()
        
        # If question has sufficient details or analytical verbs, do not trigger clarification
        analytical_keywords = [
            "分析", "統計", "比較", "找出", "列出", "查詢", "顯示", "計算", "排名", "預警", "高於", "低於",
            "compare", "find", "show", "list", "calculate", "where", "group", "top", "rank", "sum", "avg", "count"
        ]
        if any(kw in q_clean for kw in analytical_keywords):
            return False, "NONE", []

        # Only trigger for truly short/vague 1-2 words queries
        words = q_clean.split()
        if (len(words) <= 2 and len(q_clean) <= 6) or len(q_clean) <= 3:
            for keyword, (amb_type, options) in self.AMBIGUOUS_PATTERNS.items():
                if keyword in q_clean:
                    return True, amb_type, options
            return True, "metric", ["Revenue Growth", "Total Orders", "Product Return Rate"]
            
        return False, "NONE", []


ambiguity_detector = AmbiguityDetector()
