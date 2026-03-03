from backend.services.ledger_engine import LedgerEngine
from backend.services.masterdata_engine import MasterDataEngine


def test_post_journal_writes_postings_and_marks_posted(tmp_path):
    master = MasterDataEngine(tmp_path)
    master.create_account("1100", "Accounts Receivable", "ASSET")
    master.create_account("4000", "Sales", "INCOME")

    engine = LedgerEngine(tmp_path)
    result = engine.create_and_post_journal(
        date="2026-01-10",
        memo="Sale",
        reference="INV-1",
        lines=[
            {"account_id": "1100", "debit": 100.0, "credit": 0.0},
            {"account_id": "4000", "debit": 0.0, "credit": 100.0},
        ],
    )
    assert result["status"] == "POSTED"
    assert len(result["lines"]) == 2
    assert len(engine.postings.read_all()) == 2
