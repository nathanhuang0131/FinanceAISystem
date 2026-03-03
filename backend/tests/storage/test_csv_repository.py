from backend.storage.bootstrap import init_data_dirs


def test_bootstrap_creates_expected_csv_files(tmp_path):
    init_data_dirs(tmp_path)
    assert (tmp_path / "masterdata" / "customers.csv").exists()
    assert (tmp_path / "masterdata" / "chart_of_accounts.csv").exists()
    assert (tmp_path / "ledger" / "postings.csv").exists()
