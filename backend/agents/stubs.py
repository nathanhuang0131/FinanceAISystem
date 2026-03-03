from __future__ import annotations


def categorize_transaction(text: str) -> dict[str, str]:
    text_lower = text.lower()
    if "rent" in text_lower:
        category = "rent_expense"
    elif "salary" in text_lower or "payroll" in text_lower:
        category = "payroll_expense"
    elif "invoice" in text_lower or "sale" in text_lower:
        category = "sales_income"
    else:
        category = "uncategorized"
    return {"category": category, "reason": "deterministic_keyword_match"}


def summarize_statement(report_payload: dict[str, object]) -> dict[str, str]:
    keys = ", ".join(sorted(report_payload.keys()))
    return {
        "summary": f"Deterministic summary generated from keys: {keys}",
        "mode": "stub",
    }
