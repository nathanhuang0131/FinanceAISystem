# Finance Backend Replacement Design

**Date:** 2026-03-02
**Scope:** Full replacement of `backend/` with CSV-backed accounting v1

## Goals
- Deliver an end-to-end, deterministic accounting backend with FastAPI + CLI.
- Use CSV persistence only (no DB, no Docker).
- Provide tested journal posting, reporting, and master data CRUD.

## Architecture
- `backend/app/`: FastAPI application factory, routers, request/response schemas.
- `backend/orchestrator/`: workflow coordinator for create+validate+post journal.
- `backend/services/`:
  - `masterdata_engine.py`: CRUD + validation for customers, suppliers, COA, tax codes.
  - `ledger_engine.py`: draft journal creation, line checks, posting to immutable ledger.
  - `statement_engine.py`: trial balance, P&L, balance sheet, cashflow placeholder.
- `backend/compliance/`: hard accounting checks and rule helpers.
- `backend/storage/`: CSV repository interfaces and concrete file-backed implementation.
- `backend/agents/`: deterministic stubs for categorization and statement summaries.
- `backend/tests/`: service tests + API integration tests + CLI flow checks.

Dependency direction: `app -> orchestrator -> services -> storage`, with compliance used by orchestrator/services.

## Data Model (CSV)
- Master data:
  - `data/masterdata/customers.csv`
  - `data/masterdata/suppliers.csv`
  - `data/masterdata/chart_of_accounts.csv`
  - `data/masterdata/tax_codes.csv`
- Ledger:
  - `data/ledger/journals.csv`
  - `data/ledger/journal_lines.csv`
  - `data/ledger/postings.csv`
- Samples/output:
  - `data/samples/*.json`
  - `data/output/statements/*.csv`

## Core Flows
1. Journal post request (API/CLI) enters orchestrator.
2. Compliance validates line-level and header-level constraints.
3. Ledger engine writes draft journal and lines.
4. Posting appends immutable rows to `postings.csv` and marks journal `POSTED`.
5. Statement engine computes reports from postings + COA types.

## Error Handling
- Domain errors return clear messages (`ValueError`/custom exceptions).
- API maps domain errors to 4xx with details.
- Unknown errors map to 500.

## Testing Strategy
- Validation unit tests: balancing, non-negative amounts, account existence, one-side-only rules.
- Ledger tests: posting writes expected journal/line/posting rows.
- Statement tests: seeded dataset yields deterministic totals.
- API tests: TestClient CRUD, post journal, report endpoints.
- Cashflow placeholder test verifies stable response contract.

## Out of Scope (v2+)
- Multi-currency
- Full GST reporting
- Period close/reversal
- LLM/network integration
