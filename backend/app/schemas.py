from __future__ import annotations

from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str
    email: str | None = None
    terms: str | None = None


class SupplierCreate(BaseModel):
    name: str
    email: str | None = None


class AccountCreate(BaseModel):
    account_id: str
    name: str
    type: str = Field(pattern="^(ASSET|LIABILITY|EQUITY|INCOME|EXPENSE)$")


class TaxCodeCreate(BaseModel):
    code: str
    rate: float
    description: str = ""


class JournalLineIn(BaseModel):
    account_id: str
    debit: float = 0.0
    credit: float = 0.0
    description: str = ""
    customer_id: str | None = None
    supplier_id: str | None = None


class JournalCreate(BaseModel):
    date: str
    memo: str = ""
    reference: str = ""
    lines: list[JournalLineIn]
