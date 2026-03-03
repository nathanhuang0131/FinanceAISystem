from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from backend.services.masterdata_engine import MasterDataEngine
from backend.storage.bootstrap import LEDGER_FILES, init_data_dirs
from backend.storage.csv_repository import CsvTable


class StatementEngine:
    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path)
        init_data_dirs(self.base_path)
        self.postings = CsvTable(self.base_path / "ledger" / "postings.csv", LEDGER_FILES["postings.csv"])
        self.master_engine = MasterDataEngine(self.base_path)

    @staticmethod
    def _parse_date(value: str) -> date:
        return datetime.strptime(value, "%Y-%m-%d").date()

    def _coa_map(self) -> dict[str, dict[str, str]]:
        return {row["account_id"]: row for row in self.master_engine.list_chart_of_accounts()}

    def _filtered_postings(self, date_from: str | None = None, date_to: str | None = None) -> list[dict[str, str]]:
        rows = self.postings.read_all()
        if not date_from and not date_to:
            return rows
        lower = self._parse_date(date_from) if date_from else None
        upper = self._parse_date(date_to) if date_to else None
        filtered: list[dict[str, str]] = []
        for row in rows:
            row_date = self._parse_date(row["date"])
            if lower and row_date < lower:
                continue
            if upper and row_date > upper:
                continue
            filtered.append(row)
        return filtered

    def account_balance(self, account_id: str, date_from: str, date_to: str) -> dict[str, object]:
        debit = 0.0
        credit = 0.0
        for row in self._filtered_postings(date_from, date_to):
            if row["account_id"] != account_id:
                continue
            debit += float(row["debit"] or 0)
            credit += float(row["credit"] or 0)
        return {
            "account_id": account_id,
            "debit": debit,
            "credit": credit,
            "balance": debit - credit,
        }

    def trial_balance(self, date_from: str, date_to: str) -> dict[str, object]:
        coa = self._coa_map()
        totals: dict[str, dict[str, float]] = {}
        for row in self._filtered_postings(date_from, date_to):
            account_id = row["account_id"]
            bucket = totals.setdefault(account_id, {"debit": 0.0, "credit": 0.0})
            bucket["debit"] += float(row["debit"] or 0)
            bucket["credit"] += float(row["credit"] or 0)

        lines = []
        total_debit = 0.0
        total_credit = 0.0
        for account_id, bucket in sorted(totals.items()):
            total_debit += bucket["debit"]
            total_credit += bucket["credit"]
            account = coa.get(account_id, {"name": "Unknown", "type": "UNKNOWN"})
            lines.append(
                {
                    "account_id": account_id,
                    "account_name": account["name"],
                    "account_type": account["type"],
                    "debit": round(bucket["debit"], 2),
                    "credit": round(bucket["credit"], 2),
                    "balance": round(bucket["debit"] - bucket["credit"], 2),
                }
            )
        return {
            "date_from": date_from,
            "date_to": date_to,
            "lines": lines,
            "total_debit": round(total_debit, 2),
            "total_credit": round(total_credit, 2),
        }

    def profit_and_loss(self, date_from: str, date_to: str) -> dict[str, object]:
        coa = self._coa_map()
        income_lines: list[dict[str, object]] = []
        expense_lines: list[dict[str, object]] = []

        by_account: dict[str, dict[str, float]] = {}
        for row in self._filtered_postings(date_from, date_to):
            account_id = row["account_id"]
            bucket = by_account.setdefault(account_id, {"debit": 0.0, "credit": 0.0})
            bucket["debit"] += float(row["debit"] or 0)
            bucket["credit"] += float(row["credit"] or 0)

        total_income = 0.0
        total_expenses = 0.0
        for account_id, bucket in by_account.items():
            account = coa.get(account_id)
            if not account:
                continue
            if account["type"] == "INCOME":
                amount = bucket["credit"] - bucket["debit"]
                total_income += amount
                income_lines.append({"account_id": account_id, "account_name": account["name"], "amount": round(amount, 2)})
            if account["type"] == "EXPENSE":
                amount = bucket["debit"] - bucket["credit"]
                total_expenses += amount
                expense_lines.append({"account_id": account_id, "account_name": account["name"], "amount": round(amount, 2)})

        return {
            "date_from": date_from,
            "date_to": date_to,
            "income": sorted(income_lines, key=lambda x: x["account_id"]),
            "expenses": sorted(expense_lines, key=lambda x: x["account_id"]),
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(total_income - total_expenses, 2),
        }

    def balance_sheet(self, as_of: str) -> dict[str, object]:
        coa = self._coa_map()
        by_account: dict[str, dict[str, float]] = {}
        for row in self._filtered_postings(date_to=as_of):
            account_id = row["account_id"]
            bucket = by_account.setdefault(account_id, {"debit": 0.0, "credit": 0.0})
            bucket["debit"] += float(row["debit"] or 0)
            bucket["credit"] += float(row["credit"] or 0)

        assets: list[dict[str, object]] = []
        liabilities: list[dict[str, object]] = []
        equity: list[dict[str, object]] = []
        total_assets = 0.0
        total_liabilities = 0.0
        total_equity = 0.0

        for account_id, bucket in by_account.items():
            account = coa.get(account_id)
            if not account:
                continue
            account_type = account["type"]
            if account_type == "ASSET":
                amount = bucket["debit"] - bucket["credit"]
                total_assets += amount
                assets.append({"account_id": account_id, "account_name": account["name"], "amount": round(amount, 2)})
            elif account_type == "LIABILITY":
                amount = bucket["credit"] - bucket["debit"]
                total_liabilities += amount
                liabilities.append({"account_id": account_id, "account_name": account["name"], "amount": round(amount, 2)})
            elif account_type == "EQUITY":
                amount = bucket["credit"] - bucket["debit"]
                total_equity += amount
                equity.append({"account_id": account_id, "account_name": account["name"], "amount": round(amount, 2)})

        return {
            "as_of": as_of,
            "assets": sorted(assets, key=lambda x: x["account_id"]),
            "liabilities": sorted(liabilities, key=lambda x: x["account_id"]),
            "equity": sorted(equity, key=lambda x: x["account_id"]),
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "total_equity": round(total_equity, 2),
            "liabilities_plus_equity": round(total_liabilities + total_equity, 2),
        }

    def cashflow_placeholder(self, date_from: str, date_to: str) -> dict[str, str]:
        return {
            "status": "not_implemented",
            "message": "Cashflow statement not implemented yet",
            "todo": "Implement indirect method cashflow in v2",
            "date_from": date_from,
            "date_to": date_to,
        }
