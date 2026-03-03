from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from backend.storage.bootstrap import MASTERDATA_FILES, init_data_dirs
from backend.storage.csv_repository import CsvTable

ACCOUNT_TYPES = {"ASSET", "LIABILITY", "EQUITY", "INCOME", "EXPENSE"}


class MasterDataEngine:
    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path)
        init_data_dirs(self.base_path)
        master_path = self.base_path / "masterdata"
        self.customers = CsvTable(master_path / "customers.csv", MASTERDATA_FILES["customers.csv"])
        self.suppliers = CsvTable(master_path / "suppliers.csv", MASTERDATA_FILES["suppliers.csv"])
        self.coa = CsvTable(master_path / "chart_of_accounts.csv", MASTERDATA_FILES["chart_of_accounts.csv"])
        self.tax_codes = CsvTable(master_path / "tax_codes.csv", MASTERDATA_FILES["tax_codes.csv"])

    @staticmethod
    def _now() -> str:
        return datetime.utcnow().isoformat()

    def create_customer(self, name: str, email: str | None = None, terms: str | None = None) -> dict[str, str]:
        if not name.strip():
            raise ValueError("Customer name is required")
        customer_id = uuid4().hex[:10]
        row = {
            "id": customer_id,
            "name": name.strip(),
            "email": (email or "").strip(),
            "terms": (terms or "").strip(),
            "created_at": self._now(),
        }
        self.customers.append(row)
        return row

    def list_customers(self) -> list[dict[str, str]]:
        return self.customers.read_all()

    def create_supplier(self, name: str, email: str | None = None) -> dict[str, str]:
        if not name.strip():
            raise ValueError("Supplier name is required")
        supplier_id = uuid4().hex[:10]
        row = {
            "id": supplier_id,
            "name": name.strip(),
            "email": (email or "").strip(),
            "created_at": self._now(),
        }
        self.suppliers.append(row)
        return row

    def list_suppliers(self) -> list[dict[str, str]]:
        return self.suppliers.read_all()

    def create_account(self, account_id: str, name: str, account_type: str) -> dict[str, str]:
        account_id = account_id.strip()
        account_type = account_type.strip().upper()
        if not account_id:
            raise ValueError("account_id is required")
        if not name.strip():
            raise ValueError("Account name is required")
        if account_type not in ACCOUNT_TYPES:
            raise ValueError("Invalid account type")
        if self.coa.find_one("account_id", account_id):
            raise ValueError(f"Account '{account_id}' already exists")
        row = {
            "account_id": account_id,
            "name": name.strip(),
            "type": account_type,
            "created_at": self._now(),
        }
        self.coa.append(row)
        return row

    def list_chart_of_accounts(self) -> list[dict[str, str]]:
        return self.coa.read_all()

    def create_tax_code(self, code: str, rate: float, description: str) -> dict[str, str]:
        code = code.strip().upper()
        if not code:
            raise ValueError("Tax code is required")
        if self.tax_codes.find_one("code", code):
            raise ValueError(f"Tax code '{code}' already exists")
        row = {
            "code": code,
            "rate": f"{float(rate):.4f}",
            "description": description.strip(),
            "created_at": self._now(),
        }
        self.tax_codes.append(row)
        return row

    def list_tax_codes(self) -> list[dict[str, str]]:
        return self.tax_codes.read_all()
