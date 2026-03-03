# Finance AI Monorepo — Project Summary, Architecture, Codex Prompt, and Setup Instructions

_Last updated: 2026-03-02 (Australia/Sydney)_

## 1) What we’re building (key points from our discussions)

You want a **Python-first Finance AI system** that can run locally (Windows + Conda Prompt) and later on a VM, with:

- **Monorepo structure** (`finance-ai-monorepo/`) containing:
  - `frontend/` (optional early; can be terminal UI first, then Next.js later)
  - `backend/` (FastAPI app)
  - `backend/agents/` (LLM-style agents; start stubbed/mocked if no LLM key yet)
  - `backend/services/` (deterministic “engines” like accounting rules, statement generation)
  - `backend/orchestrator/` (routing/workflows between services + agents)
  - `backend/compliance/` (policy checks, validation rules)
  - `packages/` (shared schemas/types/SDK; optional)
  - `infra/` (Docker later; you currently don’t use Docker)

- **No Docker required initially.**
- **No database required initially**: store data in **CSV (or SQLite optional later)**.
- Must be **wired end-to-end**, with:
  - clear folder layout
  - runnable backend
  - deterministic accounting functions tested
  - API routes connected to the engines
  - CLI/terminal UI to exercise main flows

### Core accounting features you explicitly want

A minimal accounting / resource management foundation that supports:

- **Journal posting**
  - Create journal entries with multiple lines (debits/credits)
  - Validate balancing rules (total debits == total credits)
  - Post to ledger

- **Analysis**
  - Trial balance
  - Account balances by date range
  - Basic P&L / Balance Sheet views

- **Statement generation**
  - Income Statement (P&L)
  - Balance Sheet
  - Cashflow statement (basic indirect method can be staged; start with placeholder if needed)

- **Master data**
  - Customers
  - Suppliers
  - Chart of Accounts
  - Items/Products (optional)
  - Tax codes / GST (AU-ready structure; implement minimal first)

- **Accounting system requirements**
  - Period / close controls (phase 2)
  - Audit trail (at least append-only ledger + timestamps)
  - Deterministic validation and compliance checks

---

## 2) Architecture (finance-ai system)

### 2.1 High-level component view

**Frontend / UI**
- Phase 1: Terminal UI (Typer or Rich)
- Phase 2: Web UI (Next.js) hitting FastAPI

**Backend (FastAPI)**
- Exposes REST endpoints for:
  - master data CRUD
  - journal entry create/post
  - ledger queries
  - statement generation

**Services (deterministic engines)**
- `ledger_engine`: posting rules, balances, trial balance
- `statement_engine`: P&L, Balance Sheet, Cashflow
- `masterdata_engine`: validation, uniqueness, lookups

**Orchestrator**
- Coordinates multi-step workflows:
  - “Create customer + opening balance + post entry”
  - “Import CSV bank feed -> map -> propose journals -> user approve -> post”

**Agents**
- Initially stubs, later LLM-enabled:
  - classify transactions
  - suggest account mapping
  - summarize monthly performance
  - detect anomalies
- IMPORTANT: keep **deterministic services as source-of-truth**, agents propose, services validate.

**Compliance**
- Hard rules + checks:
  - journals balance
  - COA account type constraints
  - locked period rules
  - basic tax validation

### 2.2 Data storage (Phase 1)

CSV-backed repositories:
- `data/masterdata/customers.csv`
- `data/masterdata/suppliers.csv`
- `data/masterdata/chart_of_accounts.csv`
- `data/ledger/journals.csv` (journal headers)
- `data/ledger/journal_lines.csv` (journal lines)
- `data/ledger/postings.csv` (final ledger postings / lines)
- `data/output/statements/` (generated statement CSVs)

Later upgrade path:
- SQLite (local)
- Postgres (VM/cloud)

---

## 3) Codex prompt (copy/paste into Codex CLI)

> **Goal:** Have Codex create the initial repo skeleton + fully wired minimal accounting backend + CLI + tests.

### 3.1 Master prompt

**System context (include in one Codex task):**

You are coding a Finance AI monorepo on Windows. The user uses Conda Prompt. Do NOT use Docker. Do NOT require a database. Use CSV files for persistence. Implement a minimal but end-to-end working accounting system with deterministic engines and a thin orchestration layer, plus a simple terminal UI, and comprehensive unit tests. Ensure all tests pass.

**Repo target structure:**
- finance-ai-monorepo/
  - backend/
    - app/ (FastAPI app)
    - services/ (deterministic engines)
    - compliance/
    - orchestrator/
    - agents/ (stubs; no external LLM calls yet)
    - storage/ (CSV repositories)
    - tests/
  - frontend/ (optional stub folder only; do not implement yet)
  - data/ (CSV data folders created at runtime if missing)
  - scripts/ (dev scripts)
  - README.md

**Functional requirements:**
1. Master data CRUD:
   - Customers (id, name, email optional, terms optional)
   - Suppliers (id, name, email optional)
   - Chart of Accounts (account_id, name, type: ASSET/LIABILITY/EQUITY/INCOME/EXPENSE)
   - Tax codes (code, rate, description) minimal

2. Journal posting:
   - Create draft journal (date, memo, reference)
   - Add journal lines (account_id, debit, credit, description, optional customer_id/supplier_id)
   - Validate: debit/credit non-negative; one side only; totals balance; account exists.
   - Post journal -> writes postings (immutable ledger lines) and sets journal status POSTED.

3. Queries/analysis:
   - Trial balance by date range
   - Account balance by date range
   - Journal list + journal detail

4. Statements:
   - Profit & Loss (by date range): income - expenses, grouped by account
   - Balance Sheet (as-of date): assets, liabilities, equity totals
   - Cashflow: can be a simple placeholder returning “not implemented” with a clear TODO, but include tests expecting that placeholder response (so tests still pass). If you can implement a basic indirect method, do so, but prioritize correctness and testability.

5. Orchestrator:
   - Provide a simple “workflow” function that:
     - Accepts a JSON payload for a journal + lines
     - Validates via compliance
     - Calls ledger_engine to post
     - Returns result

6. Agents (stubs):
   - Provide an interface for “transaction categorizer” and “statement summarizer” that currently returns deterministic placeholder outputs.
   - Ensure no network calls.

7. Terminal UI:
   - Typer-based CLI (or Click), commands:
     - `init-data` (create folders/seed COA)
     - `add-customer`, `add-supplier`
     - `post-journal` (from JSON file path)
     - `trial-balance`
     - `pnl`
     - `balance-sheet`

8. FastAPI:
   - Endpoints:
     - POST /customers, GET /customers
     - POST /suppliers, GET /suppliers
     - POST /coa, GET /coa
     - POST /journals (create+post in one call acceptable for v1)
     - GET /journals, GET /journals/{id}
     - GET /reports/trial-balance
     - GET /reports/pnl
     - GET /reports/balance-sheet
   - Use Pydantic models for request/response.
   - Add OpenAPI tags.

9. Testing:
   - Pytest tests for:
     - validation rules
     - posting writes CSVs correctly
     - statements produce expected totals for a known seeded dataset
     - API endpoints basic integration tests (FastAPI TestClient)

10. Quality:
   - Clean module boundaries: API -> orchestrator -> services/storage
   - Robust error messages
   - Use type hints, ruff/black compatible formatting if possible
   - Ensure `pytest` passes on a fresh clone after `pip install -r requirements.txt`.

**Deliverables:**
- All code created in the repo above
- requirements.txt
- README.md with exact run commands
- A Windows-friendly dev script (e.g., `scripts/dev.ps1`) to run API and tests
- Seed sample data and sample journal JSON files in `data/samples/`

**Do the work now**: create/modify files as needed, run tests, fix failures until green. Provide a short summary of what was created and how to run it.

---

## 4) What you need to prepare so Codex runs properly

### 4.1 Local prerequisites
- Windows + **Conda Prompt**
- Git installed
- Python 3.10+ recommended
- Node.js not required for phase 1 (frontend optional)

### 4.2 Create a clean Conda environment (recommended)
Example (Conda Prompt):

```bash
conda create -n finance-ai python=3.11 -y
conda activate finance-ai
python -V
```

### 4.3 Repo location
Choose a folder like:

```bash
cd C:\Users\<you>\Projects
mkdir finance-ai-monorepo
cd finance-ai-monorepo
git init
```

(Or let Codex create/init the repo. Either approach is fine—just be consistent.)

---

## 5) “Wired and working” checklist (what to verify)

After Codex generates the code, verify in this exact order:

1. **Install deps**
```bash
pip install -r requirements.txt
```

2. **Run unit tests**
```bash
pytest -q
```
Expected: all green.

3. **Init seed data**
```bash
python -m backend.cli init-data
```

4. **Add master data**
```bash
python -m backend.cli add-customer --name "Acme Pty Ltd"
python -m backend.cli add-supplier --name "Widgets Co"
```

5. **Post a sample journal**
```bash
python -m backend.cli post-journal --path data/samples/sample_journal.json
```

6. **Run reports**
```bash
python -m backend.cli trial-balance --from 2026-01-01 --to 2026-12-31
python -m backend.cli pnl --from 2026-01-01 --to 2026-12-31
python -m backend.cli balance-sheet --asof 2026-12-31
```

7. **Run the API**
```bash
uvicorn backend.app.main:app --reload
```

Open API docs:
- http://127.0.0.1:8000/docs

8. **API smoke test**
- Create a customer via `/customers`
- Post a journal via `/journals`
- Run `/reports/pnl`

---

## 6) Suggested v1 scope boundaries (to keep it shippable)

Include now:
- Balanced journals
- CSV storage
- Trial balance / P&L / Balance Sheet
- Master data basics

Defer (v2+):
- Multi-currency
- Full tax/GST reporting
- Period close + reversing journals
- Bank feed ingestion + matching
- True LLM integration (keep stubs only in v1)

---

## 7) Notes for future upgrades

- Swap CSV repositories -> SQLite repositories behind the same interface.
- Add an event log / audit log file for compliance.
- Add role-based access later if you deploy to a VM.
- Add ingestion agent pipeline once file ingestion is needed.
