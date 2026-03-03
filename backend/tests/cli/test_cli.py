from typer.testing import CliRunner

import backend.cli as cli


def test_init_data_command(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "DATA_ROOT", tmp_path)
    result = CliRunner().invoke(cli.app, ["init-data"])
    assert result.exit_code == 0
    assert (tmp_path / "masterdata" / "customers.csv").exists()
