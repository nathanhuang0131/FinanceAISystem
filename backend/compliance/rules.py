from __future__ import annotations

from math import isclose


def validate_journal_lines(lines: list[dict[str, object]], existing_accounts: set[str]) -> None:
    if not lines:
        raise ValueError("Journal must contain at least one line")

    total_debit = 0.0
    total_credit = 0.0

    for index, line in enumerate(lines, start=1):
        account_id = str(line.get("account_id", "")).strip()
        if not account_id:
            raise ValueError(f"Line {index}: account_id is required")
        if account_id not in existing_accounts:
            raise ValueError(f"Line {index}: account_id '{account_id}' does not exist")

        debit = float(line.get("debit", 0) or 0)
        credit = float(line.get("credit", 0) or 0)

        if debit < 0 or credit < 0:
            raise ValueError(f"Line {index}: debit/credit must be non-negative")
        if (debit > 0 and credit > 0) or (debit == 0 and credit == 0):
            raise ValueError(f"Line {index}: exactly one of debit or credit must be greater than zero")

        total_debit += debit
        total_credit += credit

    if not isclose(total_debit, total_credit, rel_tol=0.0, abs_tol=1e-6):
        raise ValueError("Journal is not balanced: total debits must equal total credits")
