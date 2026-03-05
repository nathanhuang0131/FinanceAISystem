# Document Ingestion OCR Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete PDF ingestion flow with native extraction, PaddleOCR fallback, persisted artifacts, and structured schema extraction API with passing offline tests.

**Architecture:** Extend the existing FastAPI backend with a dedicated ingest router, storage helper, scan service, and structure service. Keep existing accounting routes untouched to minimize regression risk. Persist deterministic artifacts under `data/uploads/<doc_id>/extracted` and run OCR conditionally per page.

**Tech Stack:** FastAPI, Pydantic v2, pytest, pypdf, pdfplumber, PyMuPDF, Pillow, NumPy, PaddleOCR/PaddlePaddle.

---

### Task 1: Baseline dependency/import stability

**Files:**
- Modify: `C:/Users/User/Documents/finance-ai-monorepo/requirements.txt`
- Verify: `C:/Users/User/Documents/finance-ai-monorepo/backend/__init__.py`
- Verify: `C:/Users/User/Documents/finance-ai-monorepo/pytest.ini`

**Step 1: Write failing baseline checks**
- Run `python -c "import backend; print('backend import ok')"` and `pytest -q`.

**Step 2: Run check to verify failures (if any)**
- Expected: dependency/import errors before fixes.

**Step 3: Write minimal requirement updates**
- Add required packages for ingest + OCR.

**Step 4: Run checks to verify baseline green**
- Run baseline commands again.

### Task 2: Upload storage contract

**Files:**
- Create: `C:/Users/User/Documents/finance-ai-monorepo/backend/storage/uploads.py`
- Test: `C:/Users/User/Documents/finance-ai-monorepo/backend/tests/ingest/test_upload_storage.py`

**Step 1: Write failing tests**
- Verify deterministic folder/file layout and JSON read/write.

**Step 2: Run test to verify failure**
- `pytest -q backend/tests/ingest/test_upload_storage.py`

**Step 3: Write minimal implementation**
- Implement `create_doc_dir`, `save_original`, `write_json`, `read_json`, `get_doc_paths`.

**Step 4: Run test to verify pass**
- Re-run test.

### Task 3: Document scan engine

**Files:**
- Create: `C:/Users/User/Documents/finance-ai-monorepo/backend/services/document_scan_engine.py`
- Test: `C:/Users/User/Documents/finance-ai-monorepo/backend/tests/ingest/test_document_scan_engine.py`

**Step 1: Write failing tests**
- Generate text PDF and image-based scanned PDF in tests.
- Assert native text extraction, OCR fallback behavior, artifacts, and summary.

**Step 2: Run tests to verify failure**
- `pytest -q backend/tests/ingest/test_document_scan_engine.py`

**Step 3: Write minimal implementation**
- Implement `extract_native`, `render_pages`, `ocr_pages`, `scan` with OCR optional/missing handling.

**Step 4: Run tests to verify pass**
- Re-run test file.

### Task 4: Structured extraction engine

**Files:**
- Create: `C:/Users/User/Documents/finance-ai-monorepo/backend/services/structure_engine.py`
- Test: `C:/Users/User/Documents/finance-ai-monorepo/backend/tests/ingest/test_structure_engine.py`

**Step 1: Write failing tests**
- Validate stub outputs against Pydantic schemas.

**Step 2: Run tests to verify failure**
- `pytest -q backend/tests/ingest/test_structure_engine.py`

**Step 3: Write minimal implementation**
- Add `InvoiceSchema`, `BankStatementSchema`, `ReceiptSchema` and `structure(...)` with `stub|llm` modes.

**Step 4: Run tests to verify pass**
- Re-run test file.

### Task 5: Ingest FastAPI routes + app wiring

**Files:**
- Create: `C:/Users/User/Documents/finance-ai-monorepo/backend/app/routes/ingest.py`
- Modify: `C:/Users/User/Documents/finance-ai-monorepo/backend/app/main.py`
- Modify: `C:/Users/User/Documents/finance-ai-monorepo/backend/app/routes.py`
- Test: `C:/Users/User/Documents/finance-ai-monorepo/backend/tests/ingest/test_ingest_api.py`

**Step 1: Write failing API tests**
- Cover upload/scan/get/artifact/structure endpoints.

**Step 2: Run tests to verify failure**
- `pytest -q backend/tests/ingest/test_ingest_api.py`

**Step 3: Write minimal implementation**
- Add router + endpoint logic and mount without breaking existing routes.

**Step 4: Run tests to verify pass**
- Re-run test file.

### Task 6: Documentation + full verification + integration

**Files:**
- Modify: `C:/Users/User/Documents/finance-ai-monorepo/README.md`
- Modify: `C:/Users/User/Documents/finance-ai-monorepo/User-manual.md` (create if absent)

**Step 1: Update docs**
- Add Windows/Conda setup, OCR behavior, artifacts path, curl + PowerShell examples.

**Step 2: Run full verification**
- `pip install -r requirements.txt`
- `python -c "import paddle; import paddleocr; print('paddle ok')"`
- `pytest -q`

**Step 3: Commit and push**
- Commit only relevant files and push to `master` on `https://github.com/nathanhuang0131/FinanceAISystem.git`.
