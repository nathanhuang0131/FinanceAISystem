from backend.agents.stubs import categorize_transaction, summarize_statement


def test_categorizer_stub_returns_deterministic_category() -> None:
    result = categorize_transaction("Monthly rent invoice")
    assert result["category"] == "rent_expense"


def test_summary_stub_returns_deterministic_summary() -> None:
    result = summarize_statement({"net_profit": 100})
    assert result["mode"] == "stub"
