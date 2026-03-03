from backend.services.masterdata_engine import MasterDataEngine
from backend.orchestrator.workflows import create_and_post_journal_workflow


def test_create_and_post_workflow_returns_posted_status(tmp_path):
    master = MasterDataEngine(tmp_path)
    master.create_account("1100", "Accounts Receivable", "ASSET")
    master.create_account("4000", "Sales", "INCOME")

    result = create_and_post_journal_workflow(
        tmp_path,
        {
            "date": "2026-01-10",
            "memo": "Sale",
            "reference": "INV-1",
            "lines": [
                {"account_id": "1100", "debit": 100, "credit": 0},
                {"account_id": "4000", "debit": 0, "credit": 100},
            ],
        },
    )
    assert result["status"] == "POSTED"
