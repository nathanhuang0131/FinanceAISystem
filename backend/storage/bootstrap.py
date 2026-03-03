from __future__ import annotations

import csv
from pathlib import Path

MASTERDATA_FILES: dict[str, list[str]] = {
    "customers.csv": ["id", "name", "email", "terms", "created_at"],
    "suppliers.csv": ["id", "name", "email", "created_at"],
    "chart_of_accounts.csv": ["account_id", "name", "type", "created_at"],
    "tax_codes.csv": ["code", "rate", "description", "created_at"],
}

LEDGER_FILES: dict[str, list[str]] = {
    "journals.csv": ["journal_id", "date", "memo", "reference", "status", "created_at", "posted_at"],
    "journal_lines.csv": [
        "line_id",
        "journal_id",
        "account_id",
        "debit",
        "credit",
        "description",
        "customer_id",
        "supplier_id",
    ],
    "postings.csv": [
        "posting_id",
        "journal_id",
        "line_id",
        "date",
        "account_id",
        "debit",
        "credit",
        "description",
        "customer_id",
        "supplier_id",
        "posted_at",
    ],
}


def _write_header_if_missing(path: Path, headers: list[str]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()


def init_data_dirs(base_path: Path) -> None:
    base_path = Path(base_path)
    (base_path / "masterdata").mkdir(parents=True, exist_ok=True)
    (base_path / "ledger").mkdir(parents=True, exist_ok=True)
    (base_path / "output" / "statements").mkdir(parents=True, exist_ok=True)
    for filename, headers in MASTERDATA_FILES.items():
        _write_header_if_missing(base_path / "masterdata" / filename, headers)
    for filename, headers in LEDGER_FILES.items():
        _write_header_if_missing(base_path / "ledger" / filename, headers)
