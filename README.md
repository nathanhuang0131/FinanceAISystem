# Finance AI Monorepo (v1 CSV Backend)

## Setup (Windows + Conda Prompt)

```bash
conda create -n finance-ai python=3.11 -y
conda activate finance-ai
pip install -r requirements.txt
```

## Run Tests

```bash
pytest -q
```

## Initialize Data

```bash
python -m backend.cli init-data
```

## CLI Usage

```bash
python -m backend.cli add-customer --name "Acme Pty Ltd"
python -m backend.cli add-supplier --name "Widgets Co"
python -m backend.cli post-journal --path data/samples/sample_journal.json
python -m backend.cli trial-balance --from 2026-01-01 --to 2026-12-31
python -m backend.cli pnl --from 2026-01-01 --to 2026-12-31
python -m backend.cli balance-sheet --asof 2026-12-31
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
- `GET /reports/cashflow?from=YYYY-MM-DD&to=YYYY-MM-DD` (placeholder)

## Dev Script

```bash
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1
```
