import pytest

from backend.compliance.rules import validate_journal_lines


def test_rejects_unbalanced_journal() -> None:
    with pytest.raises(ValueError, match="debits"):
        validate_journal_lines(
            [
                {"account_id": "1000", "debit": 100, "credit": 0},
                {"account_id": "2000", "debit": 0, "credit": 50},
            ],
            existing_accounts={"1000", "2000"},
        )


def test_rejects_missing_account() -> None:
    with pytest.raises(ValueError, match="does not exist"):
        validate_journal_lines(
            [{"account_id": "9999", "debit": 10, "credit": 0}],
            existing_accounts={"1000"},
        )
