from fastapi.testclient import TestClient

from backend.app import deps
from backend.app.main import app


def test_post_customer_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(deps, "DATA_ROOT", tmp_path)
    client = TestClient(app)
    resp = client.post("/customers", json={"name": "Acme Pty Ltd"})
    assert resp.status_code == 201
    listed = client.get("/customers")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_post_journal_and_fetch_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(deps, "DATA_ROOT", tmp_path)
    client = TestClient(app)

    assert client.post("/coa", json={"account_id": "1000", "name": "Cash", "type": "ASSET"}).status_code == 201
    assert client.post("/coa", json={"account_id": "4000", "name": "Sales", "type": "INCOME"}).status_code == 201

    payload = {
        "date": "2026-01-10",
        "memo": "Sale",
        "reference": "INV-1",
        "lines": [
            {"account_id": "1000", "debit": 100.0, "credit": 0.0},
            {"account_id": "4000", "debit": 0.0, "credit": 100.0},
        ],
    }
    created = client.post("/journals", json=payload)
    assert created.status_code == 201

    pnl = client.get("/reports/pnl", params={"from": "2026-01-01", "to": "2026-12-31"})
    assert pnl.status_code == 200
    assert pnl.json()["net_profit"] == 100.0
