from backend.services.ledger_engine import LedgerEngine
from backend.services.masterdata_engine import MasterDataEngine
from backend.services.statement_engine import StatementEngine


def _seed_postings(tmp_path):
    master = MasterDataEngine(tmp_path)
    master.create_account("1000", "Cash", "ASSET")
    master.create_account("3000", "Owner Equity", "EQUITY")
    master.create_account("4000", "Sales", "INCOME")
    master.create_account("5000", "Rent Expense", "EXPENSE")

    ledger = LedgerEngine(tmp_path)
    ledger.create_and_post_journal(
        date="2026-01-01",
        memo="Capital",
        reference="CAP-1",
        lines=[
            {"account_id": "1000", "debit": 1000, "credit": 0},
            {"account_id": "3000", "debit": 0, "credit": 1000},
        ],
    )
    ledger.create_and_post_journal(
        date="2026-01-05",
        memo="Sale",
        reference="INV-1",
        lines=[
            {"account_id": "1000", "debit": 300, "credit": 0},
            {"account_id": "4000", "debit": 0, "credit": 300},
        ],
    )
    ledger.create_and_post_journal(
        date="2026-01-07",
        memo="Rent",
        reference="BILL-1",
        lines=[
            {"account_id": "5000", "debit": 120, "credit": 0},
            {"account_id": "1000", "debit": 0, "credit": 120},
        ],
    )


def test_pnl_totals_from_seeded_postings(tmp_path):
    _seed_postings(tmp_path)
    engine = StatementEngine(tmp_path)
    report = engine.profit_and_loss(date_from="2026-01-01", date_to="2026-12-31")
    assert report["total_income"] == 300.0
    assert report["total_expenses"] == 120.0
    assert report["net_profit"] == 180.0


def test_balance_sheet_totals(tmp_path):
    _seed_postings(tmp_path)
    engine = StatementEngine(tmp_path)
    report = engine.balance_sheet(as_of="2026-12-31")
    assert report["total_assets"] == 1180.0
    assert report["liabilities_plus_equity"] == 1000.0


def test_cashflow_placeholder_contract(tmp_path):
    engine = StatementEngine(tmp_path)
    report = engine.cashflow_placeholder("2026-01-01", "2026-12-31")
    assert report["status"] == "not_implemented"
