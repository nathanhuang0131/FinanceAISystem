from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from backend.compliance.rules import validate_journal_lines
from backend.services.masterdata_engine import MasterDataEngine
from backend.storage.bootstrap import LEDGER_FILES, init_data_dirs
from backend.storage.csv_repository import CsvTable


class LedgerEngine:
    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path)
        init_data_dirs(self.base_path)
        ledger_path = self.base_path / "ledger"
        self.journals = CsvTable(ledger_path / "journals.csv", LEDGER_FILES["journals.csv"])
        self.journal_lines = CsvTable(ledger_path / "journal_lines.csv", LEDGER_FILES["journal_lines.csv"])
        self.postings = CsvTable(ledger_path / "postings.csv", LEDGER_FILES["postings.csv"])
        self.master_engine = MasterDataEngine(self.base_path)

    @staticmethod
    def _now() -> str:
        return datetime.utcnow().isoformat()

    def create_journal(self, date: str, memo: str, reference: str, lines: list[dict[str, object]]) -> dict[str, object]:
        accounts = {row["account_id"] for row in self.master_engine.list_chart_of_accounts()}
        validate_journal_lines(lines, accounts)
        journal_id = uuid4().hex
        self.journals.append(
            {
                "journal_id": journal_id,
                "date": date,
                "memo": memo,
                "reference": reference,
                "status": "DRAFT",
                "created_at": self._now(),
                "posted_at": "",
            }
        )

        created_lines: list[dict[str, object]] = []
        for line in lines:
            payload = {
                "line_id": uuid4().hex,
                "journal_id": journal_id,
                "account_id": str(line.get("account_id", "")),
                "debit": float(line.get("debit", 0) or 0),
                "credit": float(line.get("credit", 0) or 0),
                "description": str(line.get("description", "")),
                "customer_id": str(line.get("customer_id", "")),
                "supplier_id": str(line.get("supplier_id", "")),
            }
            self.journal_lines.append(payload)
            created_lines.append(payload)

        return {
            "journal_id": journal_id,
            "date": date,
            "memo": memo,
            "reference": reference,
            "status": "DRAFT",
            "lines": created_lines,
        }

    def post_journal(self, journal_id: str) -> dict[str, object]:
        journal = self.journals.find_one("journal_id", journal_id)
        if not journal:
            raise ValueError(f"Journal '{journal_id}' not found")
        if journal.get("status") == "POSTED":
            raise ValueError(f"Journal '{journal_id}' is already posted")

        posted_at = self._now()
        lines = [line for line in self.journal_lines.read_all() if line.get("journal_id") == journal_id]

        for line in lines:
            self.postings.append(
                {
                    "posting_id": uuid4().hex,
                    "journal_id": journal_id,
                    "line_id": line["line_id"],
                    "date": journal["date"],
                    "account_id": line["account_id"],
                    "debit": line["debit"],
                    "credit": line["credit"],
                    "description": line.get("description", ""),
                    "customer_id": line.get("customer_id", ""),
                    "supplier_id": line.get("supplier_id", ""),
                    "posted_at": posted_at,
                }
            )

        journal["status"] = "POSTED"
        journal["posted_at"] = posted_at
        self.journals.upsert("journal_id", journal)
        return self.get_journal(journal_id)

    def create_and_post_journal(
        self,
        date: str,
        memo: str,
        reference: str,
        lines: list[dict[str, object]],
    ) -> dict[str, object]:
        created = self.create_journal(date=date, memo=memo, reference=reference, lines=lines)
        return self.post_journal(str(created["journal_id"]))

    def list_journals(self) -> list[dict[str, object]]:
        return [
            {
                "journal_id": row["journal_id"],
                "date": row["date"],
                "memo": row["memo"],
                "reference": row["reference"],
                "status": row["status"],
                "created_at": row["created_at"],
                "posted_at": row["posted_at"],
            }
            for row in self.journals.read_all()
        ]

    def get_journal(self, journal_id: str) -> dict[str, object]:
        journal = self.journals.find_one("journal_id", journal_id)
        if not journal:
            raise ValueError(f"Journal '{journal_id}' not found")
        lines = [line for line in self.journal_lines.read_all() if line.get("journal_id") == journal_id]
        return {
            "journal_id": journal["journal_id"],
            "date": journal["date"],
            "memo": journal["memo"],
            "reference": journal["reference"],
            "status": journal["status"],
            "created_at": journal["created_at"],
            "posted_at": journal["posted_at"],
            "lines": [
                {
                    "line_id": line["line_id"],
                    "account_id": line["account_id"],
                    "debit": float(line["debit"] or 0),
                    "credit": float(line["credit"] or 0),
                    "description": line.get("description", ""),
                    "customer_id": line.get("customer_id", ""),
                    "supplier_id": line.get("supplier_id", ""),
                }
                for line in lines
            ],
        }
