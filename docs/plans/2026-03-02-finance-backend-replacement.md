# Finance Backend Replacement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the current backend with a fully wired CSV-backed accounting v1 (FastAPI + CLI + tests) that passes `pytest -q`.

**Architecture:** Build strict module boundaries (`app -> orchestrator -> services -> storage`) with compliance validation and deterministic statement engines. Persist all business data in CSV files under `data/`, generate reports from immutable postings, and expose both API and CLI flows over the same orchestrated services.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, Typer, pytest

---

### Task 1: Remove legacy backend and create package skeleton

**Files:**
- Delete: `backend/api/routes.py`, `backend/main.py`, `backend/services/detector.py`, `backend/orchestrator/router.py`, `backend/agents/default_agent.py`, `backend/compliance/checks.py`, `backend/storage/csv_store.py`
- Create: `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/schemas.py`, `backend/app/deps.py`
- Create: `backend/orchestrator/__init__.py`, `backend/orchestrator/workflows.py`
- Create: `backend/services/__init__.py`, `backend/services/masterdata_engine.py`, `backend/services/ledger_engine.py`, `backend/services/statement_engine.py`
- Create: `backend/storage/__init__.py`, `backend/storage/csv_repository.py`, `backend/storage/bootstrap.py`
- Create: `backend/compliance/__init__.py`, `backend/compliance/rules.py`
- Create: `backend/agents/__init__.py`, `backend/agents/stubs.py`
- Create: `backend/tests/__init__.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_import_contract.py

def test_backend_modules_import():
    from backend.app.main import app
    assert app is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_import_contract.py -v`
Expected: FAIL with missing module/file imports.

**Step 3: Write minimal implementation**

Create empty package files and minimal `FastAPI()` app in `backend/app/main.py`.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_import_contract.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend
git commit -m "chore: replace legacy backend skeleton"
```

### Task 2: Add storage bootstrap and CSV repository primitives

**Files:**
- Create: `backend/storage/bootstrap.py`
- Create: `backend/storage/csv_repository.py`
- Test: `backend/tests/storage/test_csv_repository.py`

**Step 1: Write the failing test**

```python
# backend/tests/storage/test_csv_repository.py

def test_bootstrap_creates_expected_csv_files(tmp_path):
    from backend.storage.bootstrap import init_data_dirs
    init_data_dirs(tmp_path)
    assert (tmp_path / "masterdata" / "customers.csv").exists()
    assert (tmp_path / "ledger" / "postings.csv").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/storage/test_csv_repository.py -v`
Expected: FAIL due to missing functions/files.

**Step 3: Write minimal implementation**

Implement:
- `init_data_dirs(base_path)` creating folder tree and CSV headers.
- lightweight CSV helpers for append/read/upsert by key.

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/storage/test_csv_repository.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/storage backend/tests/storage
git commit -m "feat: add csv bootstrap and repository helpers"
```

### Task 3: Implement master data engines (customers/suppliers/COA/tax codes)

**Files:**
- Create: `backend/services/masterdata_engine.py`
- Test: `backend/tests/services/test_masterdata_engine.py`

**Step 1: Write the failing test**

```python
def test_add_and_list_customer(tmp_path):
    from backend.services.masterdata_engine import MasterDataEngine
    engine = MasterDataEngine(tmp_path)
    created = engine.create_customer(name="Acme Pty Ltd", email=None, terms=None)
    assert created["name"] == "Acme Pty Ltd"
    assert len(engine.list_customers()) == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/services/test_masterdata_engine.py -v`
Expected: FAIL on missing engine behavior.

**Step 3: Write minimal implementation**

Implement create/list methods with uniqueness and required fields for:
- customers
- suppliers
- chart of accounts (`ASSET/LIABILITY/EQUITY/INCOME/EXPENSE`)
- tax codes

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/services/test_masterdata_engine.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/services/masterdata_engine.py backend/tests/services/test_masterdata_engine.py
git commit -m "feat: implement master data engine"
```

### Task 4: Implement compliance rules for journal validation

**Files:**
- Create: `backend/compliance/rules.py`
- Test: `backend/tests/compliance/test_rules.py`

**Step 1: Write the failing test**

```python
import pytest

def test_rejects_unbalanced_journal():
    from backend.compliance.rules import validate_journal_lines
    with pytest.raises(ValueError, match="debits.*credits"):
        validate_journal_lines([
            {"account_id": "1000", "debit": 100, "credit": 0},
            {"account_id": "2000", "debit": 0, "credit": 50},
        ], existing_accounts={"1000", "2000"})
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/compliance/test_rules.py -v`
Expected: FAIL due to missing validator.

**Step 3: Write minimal implementation**

Implement validators for:
- non-negative values
- exactly one side (`debit` xor `credit`) per line
- account existence
- balanced total debits/credits

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/compliance/test_rules.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/compliance/rules.py backend/tests/compliance/test_rules.py
git commit -m "feat: add journal compliance rules"
```

### Task 5: Implement ledger engine draft + post workflow

**Files:**
- Create: `backend/services/ledger_engine.py`
- Test: `backend/tests/services/test_ledger_engine.py`

**Step 1: Write the failing test**

```python
def test_post_journal_writes_postings_and_marks_posted(tmp_path):
    from backend.services.ledger_engine import LedgerEngine
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
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/services/test_ledger_engine.py -v`
Expected: FAIL until posting implementation exists.

**Step 3: Write minimal implementation**

Implement ledger engine methods:
- create draft journal + lines
- post journal to immutable postings
- journal retrieval/listing

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/services/test_ledger_engine.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/services/ledger_engine.py backend/tests/services/test_ledger_engine.py
git commit -m "feat: add journal posting ledger engine"
```

### Task 6: Implement statement engine (trial balance, P&L, balance sheet, cashflow placeholder)

**Files:**
- Create: `backend/services/statement_engine.py`
- Test: `backend/tests/services/test_statement_engine.py`

**Step 1: Write the failing test**

```python
def test_pnl_totals_from_seeded_postings(tmp_path):
    from backend.services.statement_engine import StatementEngine
    engine = StatementEngine(tmp_path)
    report = engine.profit_and_loss(date_from="2026-01-01", date_to="2026-12-31")
    assert "net_profit" in report
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/services/test_statement_engine.py -v`
Expected: FAIL due to missing report calculations.

**Step 3: Write minimal implementation**

Implement:
- `trial_balance(date_from, date_to)`
- `account_balance(account_id, date_from, date_to)`
- `profit_and_loss(date_from, date_to)`
- `balance_sheet(as_of)`
- `cashflow_placeholder(...)` returning stable TODO response

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/services/test_statement_engine.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/services/statement_engine.py backend/tests/services/test_statement_engine.py
git commit -m "feat: add statement engine reports"
```

### Task 7: Add orchestrator workflow and deterministic agent stubs

**Files:**
- Create: `backend/orchestrator/workflows.py`
- Create: `backend/agents/stubs.py`
- Test: `backend/tests/orchestrator/test_workflows.py`
- Test: `backend/tests/agents/test_stubs.py`

**Step 1: Write the failing test**

```python
def test_create_and_post_workflow_returns_posted_status(tmp_path):
    from backend.orchestrator.workflows import create_and_post_journal_workflow
    result = create_and_post_journal_workflow(tmp_path, {
        "date": "2026-01-10",
        "memo": "Sale",
        "reference": "INV-1",
        "lines": [
            {"account_id": "1100", "debit": 100, "credit": 0},
            {"account_id": "4000", "debit": 0, "credit": 100},
        ],
    })
    assert result["status"] == "POSTED"
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/orchestrator/test_workflows.py backend/tests/agents/test_stubs.py -v`
Expected: FAIL on missing workflow/stub contracts.

**Step 3: Write minimal implementation**

Implement:
- orchestrator function to validate then call ledger posting
- `categorize_transaction` and `summarize_statement` deterministic stub outputs

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/orchestrator/test_workflows.py backend/tests/agents/test_stubs.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/orchestrator backend/agents backend/tests/orchestrator backend/tests/agents
git commit -m "feat: add journal workflow and agent stubs"
```

### Task 8: Build FastAPI schemas/routes and wire dependencies

**Files:**
- Create: `backend/app/schemas.py`, `backend/app/deps.py`, `backend/app/routes.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/api/test_api.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from backend.app.main import app


def test_post_customer_endpoint(tmp_path, monkeypatch):
    from backend.app import deps
    monkeypatch.setattr(deps, "DATA_ROOT", tmp_path)
    client = TestClient(app)
    resp = client.post("/customers", json={"name": "Acme Pty Ltd"})
    assert resp.status_code == 201
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/api/test_api.py -v`
Expected: FAIL until endpoints/schemas are wired.

**Step 3: Write minimal implementation**

Implement required endpoints with OpenAPI tags:
- customers, suppliers, coa, journals
- reports/trial-balance, reports/pnl, reports/balance-sheet
- journal detail/list

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/api/test_api.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/app backend/tests/api/test_api.py
git commit -m "feat: add accounting api routes"
```

### Task 9: Build CLI and sample data artifacts

**Files:**
- Create: `backend/cli.py`
- Create: `data/samples/sample_journal.json`
- Create: `data/samples/seed_coa.csv`
- Test: `backend/tests/cli/test_cli.py`

**Step 1: Write the failing test**

```python
from typer.testing import CliRunner
from backend.cli import app


def test_init_data_command(tmp_path, monkeypatch):
    import backend.cli as cli
    monkeypatch.setattr(cli, "DATA_ROOT", tmp_path)
    result = CliRunner().invoke(app, ["init-data"])
    assert result.exit_code == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/cli/test_cli.py -v`
Expected: FAIL until CLI commands exist.

**Step 3: Write minimal implementation**

Implement commands:
- `init-data`
- `add-customer`
- `add-supplier`
- `post-journal --path`
- `trial-balance --from --to`
- `pnl --from --to`
- `balance-sheet --asof`

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/cli/test_cli.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/cli.py data/samples backend/tests/cli/test_cli.py
git commit -m "feat: add typer cli and sample data"
```

### Task 10: Project docs, requirements, and dev script

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `scripts/dev.ps1`
- Test: full suite `backend/tests/**`

**Step 1: Write the failing test**

```python
# backend/tests/test_repo_contract.py

def test_requirements_and_readme_exist():
    from pathlib import Path
    assert Path("requirements.txt").exists()
    assert Path("README.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_repo_contract.py -v`
Expected: FAIL until files are created.

**Step 3: Write minimal implementation**

Create:
- dependency list (`fastapi`, `uvicorn`, `pydantic`, `typer`, `pytest`, `httpx`)
- README with exact setup/run commands
- `scripts/dev.ps1` to run tests + uvicorn

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_repo_contract.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add requirements.txt README.md scripts/dev.ps1 backend/tests/test_repo_contract.py
git commit -m "docs: add setup instructions and dev script"
```

### Task 11: End-to-end verification and cleanup

**Files:**
- Modify: any failing files discovered by tests

**Step 1: Write the failing test**

No new test; use full suite as the contract.

**Step 2: Run test to verify it fails**

Run: `pytest -q`
Expected: identify any remaining failures.

**Step 3: Write minimal implementation**

Fix only failing cases, preserve scope boundaries.

**Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: all tests PASS.

**Step 5: Commit**

```bash
git add backend
# plus any touched root files
git commit -m "test: make full accounting backend suite green"
```
