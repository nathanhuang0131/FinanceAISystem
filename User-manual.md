# User Manual

## Windows Setup (Conda Prompt)

```powershell
conda create -n financeai python=3.11 -y
conda activate financeai
pip install -r requirements.txt
```

Verify OCR dependencies:

```powershell
python -c "import paddle; import paddleocr; print('paddle ok')"
```

Run backend:

```powershell
uvicorn backend.app.main:app --reload
```

## Ingestion Flow

1. Upload PDF with `POST /ingest/upload`
2. Scan with `POST /ingest/{doc_id}/scan?ocr=auto|true|false`
3. Inspect artifacts with `GET /ingest/{doc_id}/artifact`
4. Generate structured output with `POST /ingest/{doc_id}/structure`

## PowerShell Examples

Upload:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/ingest/upload" -F "file=@C:/path/to/invoice.pdf;type=application/pdf"
```

Scan (auto OCR):

```powershell
curl.exe -X POST "http://127.0.0.1:8000/ingest/<doc_id>/scan?ocr=auto"
```

Get document metadata + summary:

```powershell
curl.exe "http://127.0.0.1:8000/ingest/<doc_id>"
```

Read native text artifact:

```powershell
curl.exe "http://127.0.0.1:8000/ingest/<doc_id>/artifact?name=native_text"
```

Structure as invoice (stub mode):

```powershell
curl.exe -X POST "http://127.0.0.1:8000/ingest/<doc_id>/structure?schema=invoice&mode=stub"
```

## Artifact Location

```text
data/uploads/<doc_id>/
  original.pdf
  meta.json
  extracted/
    summary.json
    native_text.json
    native_tables.json
    ocr_text.json
    ocr_boxes.json
    structured_<schema>.json
```
