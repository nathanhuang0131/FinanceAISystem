# Finance AI Monorepo (CSV Backend + V2 Subledger)

## Setup (Windows + Conda Prompt)

```bash
conda create -n financeai python=3.11 -y
conda activate financeai
pip install -r requirements.txt
```

## Run Tests

```bash
pytest -q
```

## How To Run (Windows/Conda)

```bash
conda activate financeai
pip install -r requirements.txt
pytest -q
python -m backend.cli trial-balance --from 2026-01-01 --to 2026-01-31
python -m backend.cli pnl --from 2026-01-01 --to 2026-01-31
python -m backend.cli balance-sheet --asof 2026-01-31
python -m backend.cli cashflow --from 2026-01-01 --to 2026-01-31
```

## Initialize Data

```bash
python -m backend.cli init-data
```

## CLI Usage

```bash
python -m backend.cli add-customer --name "Acme Pty Ltd"
python -m backend.cli add-supplier --name "Widgets Co"
python -m backend.cli add-account --account-id 1000 --name "Cash" --type ASSET
python -m backend.cli post-journal --path data/samples/sample_journal.json
python -m backend.cli trial-balance --from 2026-01-01 --to 2026-12-31
python -m backend.cli pnl --from 2026-01-01 --to 2026-12-31
python -m backend.cli balance-sheet --asof 2026-12-31
python -m backend.cli cashflow --from 2026-01-01 --to 2026-12-31
```

## Cashflow (Indirect Method)

- Net profit comes from P&L over the date range.
- Non-cash addbacks currently include accounts with `depreciation` or `amort` in the expense account name.
- Working-capital adjustments include:
  - change in Accounts Receivable (`1100`) as cash effect `-delta_AR`
  - change in Accounts Payable (`2000`) as cash effect `+delta_AP`
- Output includes reconciliation fields:
  - `opening_cash`, `closing_cash`
  - `net_change_in_cash`
  - `reconciliation_diff` (target `0.0`)

## Subledger Workflows (AR/AP)

Create invoice from sample JSON:

```bash
python -m backend.cli create-invoice --path data/samples/invoice_example.json --post
python -m backend.cli list-invoices
```

Record receipt with payload file:

```bash
python -m backend.cli record-receipt --path data/samples/receipt_example.json
python -m backend.cli list-receipts
```

Create bill and record payment:

```bash
python -m backend.cli create-bill --path data/samples/bill_example.json --post
python -m backend.cli list-bills
python -m backend.cli record-payment --path data/samples/payment_example.json
python -m backend.cli list-payments
```

Lifecycle statuses auto-update by allocations:
- `OPEN` -> `PARTIAL` -> `PAID`

If an account is missing, create it first with `add-account`.

## Import / Export

Import grouped journals from CSV (`date,reference` grouping):

```bash
python -m backend.cli import-journals --csv data/samples/journals_import_example.csv --post
```

Strict mode (fail on first bad journal):

```bash
python -m backend.cli import-journals --csv data/samples/journals_import_example.csv --strict
```

Export postings to a CSV file:

```bash
python -m backend.cli export-ledger --from 2026-01-01 --to 2026-01-31 --out data/output/ledger_202601.csv
```

## Run API

```bash
uvicorn backend.app.main:app --reload
```

Open docs at `http://127.0.0.1:8000/docs`.

## API Endpoints

- `POST /customers`, `GET /customers`
- `POST /suppliers`, `GET /suppliers`
- `POST /coa`, `GET /coa`
- `POST /tax-codes`, `GET /tax-codes`
- `POST /journals`, `GET /journals`, `GET /journals/{id}`
- `GET /reports/trial-balance?from=YYYY-MM-DD&to=YYYY-MM-DD`
- `GET /reports/pnl?from=YYYY-MM-DD&to=YYYY-MM-DD`
- `GET /reports/balance-sheet?as_of=YYYY-MM-DD`
- `GET /reports/cashflow?from=YYYY-MM-DD&to=YYYY-MM-DD`
- `POST /subledger/invoices`, `GET /subledger/invoices`, `GET /subledger/invoices/{id}`
- `POST /subledger/receipts`, `GET /subledger/receipts`
- `POST /subledger/bills`, `GET /subledger/bills`, `GET /subledger/bills/{id}`
- `POST /subledger/payments`, `GET /subledger/payments`
- `POST /ingest/upload`
- `POST /ingest/{doc_id}/scan?ocr=auto|true|false`
- `GET /ingest/{doc_id}`
- `GET /ingest/{doc_id}/artifact?name=native_text|native_tables|ocr_text|summary`
- `POST /ingest/{doc_id}/structure?schema=invoice|bank_statement|receipt&mode=stub|llm`

## Document Ingestion + OCR

Artifacts are stored at:

```text
data/uploads/<doc_id>/
  original.pdf
  meta.json
  extracted/
    summary.json
    native_text.json
    native_tables.json
    ocr_text.json            # optional
    ocr_boxes.json           # optional
    structured_<schema>.json # optional
```

OCR behavior:
- `ocr=false`: native extract only
- `ocr=true`: OCR all pages
- `ocr=auto`: OCR only pages with low native text (default threshold `<50` chars)

If OCR dependencies are missing, scan returns HTTP 500 with `install paddleocr/paddlepaddle`.

## Ingest API Examples

Upload PDF:

```bash
curl -X POST "http://127.0.0.1:8000/ingest/upload" -F "file=@data/samples/invoice.pdf;type=application/pdf"
```

Scan with auto OCR:

```bash
curl -X POST "http://127.0.0.1:8000/ingest/<doc_id>/scan?ocr=auto"
```

Get summary artifact:

```bash
curl "http://127.0.0.1:8000/ingest/<doc_id>/artifact?name=summary"
```

Structured output (stub):

```bash
curl -X POST "http://127.0.0.1:8000/ingest/<doc_id>/structure?schema=invoice&mode=stub"
```

## Frontend (Next.js)

Run backend API first:

```bash
uvicorn backend.app.main:app --reload
```

Then run frontend:

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE` if the API is not on `http://127.0.0.1:8000`.

## Dev Script

```bash
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1
```
