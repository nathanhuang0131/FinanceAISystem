from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from backend.app import deps
from backend.app.schemas import AccountCreate, CustomerCreate, JournalCreate, SupplierCreate, TaxCodeCreate
from backend.orchestrator.workflows import create_and_post_journal_workflow

router = APIRouter()


@router.post("/customers", tags=["master-data"], status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate) -> dict[str, str]:
    try:
        return deps.get_master_engine().create_customer(payload.name, payload.email, payload.terms)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/customers", tags=["master-data"])
def list_customers() -> list[dict[str, str]]:
    return deps.get_master_engine().list_customers()


@router.post("/suppliers", tags=["master-data"], status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierCreate) -> dict[str, str]:
    try:
        return deps.get_master_engine().create_supplier(payload.name, payload.email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/suppliers", tags=["master-data"])
def list_suppliers() -> list[dict[str, str]]:
    return deps.get_master_engine().list_suppliers()


@router.post("/coa", tags=["master-data"], status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate) -> dict[str, str]:
    try:
        return deps.get_master_engine().create_account(payload.account_id, payload.name, payload.type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/coa", tags=["master-data"])
def list_accounts() -> list[dict[str, str]]:
    return deps.get_master_engine().list_chart_of_accounts()


@router.post("/tax-codes", tags=["master-data"], status_code=status.HTTP_201_CREATED)
def create_tax_code(payload: TaxCodeCreate) -> dict[str, str]:
    try:
        return deps.get_master_engine().create_tax_code(payload.code, payload.rate, payload.description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/tax-codes", tags=["master-data"])
def list_tax_codes() -> list[dict[str, str]]:
    return deps.get_master_engine().list_tax_codes()


@router.post("/journals", tags=["ledger"], status_code=status.HTTP_201_CREATED)
def create_post_journal(payload: JournalCreate) -> dict[str, object]:
    try:
        return create_and_post_journal_workflow(deps.get_data_root(), payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/journals", tags=["ledger"])
def list_journals() -> list[dict[str, object]]:
    return deps.get_ledger_engine().list_journals()


@router.get("/journals/{journal_id}", tags=["ledger"])
def get_journal(journal_id: str) -> dict[str, object]:
    try:
        return deps.get_ledger_engine().get_journal(journal_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/reports/trial-balance", tags=["reports"])
def trial_balance(
    date_from: str = Query(alias="from"),
    date_to: str = Query(alias="to"),
) -> dict[str, object]:
    return deps.get_statement_engine().trial_balance(date_from, date_to)


@router.get("/reports/pnl", tags=["reports"])
def pnl(
    date_from: str = Query(alias="from"),
    date_to: str = Query(alias="to"),
) -> dict[str, object]:
    return deps.get_statement_engine().profit_and_loss(date_from, date_to)


@router.get("/reports/balance-sheet", tags=["reports"])
def balance_sheet(as_of: str) -> dict[str, object]:
    return deps.get_statement_engine().balance_sheet(as_of)


@router.get("/reports/cashflow", tags=["reports"])
def cashflow(
    date_from: str = Query(alias="from"),
    date_to: str = Query(alias="to"),
) -> dict[str, str]:
    return deps.get_statement_engine().cashflow_placeholder(date_from, date_to)
