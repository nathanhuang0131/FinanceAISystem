from __future__ import annotations

import json
from pathlib import Path

import typer

from backend.app import deps
from backend.services.ledger_engine import LedgerEngine
from backend.services.masterdata_engine import MasterDataEngine
from backend.services.statement_engine import StatementEngine
from backend.storage.bootstrap import init_data_dirs

app = typer.Typer(help="Finance AI CLI")
DATA_ROOT = Path("data")


def _master() -> MasterDataEngine:
    init_data_dirs(DATA_ROOT)
    return MasterDataEngine(DATA_ROOT)


def _ledger() -> LedgerEngine:
    init_data_dirs(DATA_ROOT)
    return LedgerEngine(DATA_ROOT)


def _statements() -> StatementEngine:
    init_data_dirs(DATA_ROOT)
    return StatementEngine(DATA_ROOT)


@app.command("init-data")
def init_data() -> None:
    init_data_dirs(DATA_ROOT)
    master = _master()
    if not master.list_chart_of_accounts():
        seed_accounts = [
            ("1000", "Cash", "ASSET"),
            ("1100", "Accounts Receivable", "ASSET"),
            ("2000", "Accounts Payable", "LIABILITY"),
            ("3000", "Owner Equity", "EQUITY"),
            ("4000", "Sales", "INCOME"),
            ("5000", "Rent Expense", "EXPENSE"),
        ]
        for account_id, name, account_type in seed_accounts:
            master.create_account(account_id, name, account_type)
    typer.echo("Data initialized")


@app.command("add-customer")
def add_customer(name: str, email: str = "", terms: str = "") -> None:
    created = _master().create_customer(name=name, email=email or None, terms=terms or None)
    typer.echo(json.dumps(created))


@app.command("add-supplier")
def add_supplier(name: str, email: str = "") -> None:
    created = _master().create_supplier(name=name, email=email or None)
    typer.echo(json.dumps(created))


@app.command("post-journal")
def post_journal(path: Path = typer.Option(..., "--path")) -> None:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    result = _ledger().create_and_post_journal(
        date=payload["date"],
        memo=payload.get("memo", ""),
        reference=payload.get("reference", ""),
        lines=payload["lines"],
    )
    typer.echo(json.dumps(result))


@app.command("trial-balance")
def trial_balance(
    date_from: str = typer.Option(..., "--from"),
    date_to: str = typer.Option(..., "--to"),
) -> None:
    report = _statements().trial_balance(date_from, date_to)
    typer.echo(json.dumps(report))


@app.command("pnl")
def pnl(
    date_from: str = typer.Option(..., "--from"),
    date_to: str = typer.Option(..., "--to"),
) -> None:
    report = _statements().profit_and_loss(date_from, date_to)
    typer.echo(json.dumps(report))


@app.command("balance-sheet")
def balance_sheet(as_of: str = typer.Option(..., "--asof")) -> None:
    report = _statements().balance_sheet(as_of)
    typer.echo(json.dumps(report))


if __name__ == "__main__":
    app()
