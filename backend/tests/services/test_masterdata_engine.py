from backend.services.masterdata_engine import MasterDataEngine


def test_add_and_list_customer(tmp_path):
    engine = MasterDataEngine(tmp_path)
    created = engine.create_customer(name="Acme Pty Ltd", email=None, terms=None)
    assert created["name"] == "Acme Pty Ltd"
    assert len(engine.list_customers()) == 1


def test_add_account_and_validate_type(tmp_path):
    engine = MasterDataEngine(tmp_path)
    account = engine.create_account("1000", "Cash", "ASSET")
    assert account["type"] == "ASSET"
    assert len(engine.list_chart_of_accounts()) == 1
