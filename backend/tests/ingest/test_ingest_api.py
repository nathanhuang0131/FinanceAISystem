from __future__ import annotations

from io import BytesIO
from pathlib import Path

import fitz
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from backend.app import deps
from backend.app.main import app
from backend.services import document_scan_engine


def _text_pdf_bytes(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def _scanned_pdf_bytes(text: str) -> bytes:
    image = Image.new("RGB", (1600, 2200), "white")
    draw = ImageDraw.Draw(image)
    draw.text((100, 150), text, fill="black")

    png_buffer = BytesIO()
    image.save(png_buffer, format="PNG")
    png_bytes = png_buffer.getvalue()

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_image(page.rect, stream=png_bytes)
    data = doc.tobytes()
    doc.close()
    return data


def test_ingest_upload_stores_pdf(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(deps, "DATA_ROOT", tmp_path)
    client = TestClient(app)

    response = client.post(
        "/ingest/upload",
        files={"file": ("invoice.pdf", _text_pdf_bytes("hello"), "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert (tmp_path / "uploads" / body["doc_id"] / "original.pdf").exists()


def test_ingest_scan_ocr_false_extracts_native_text(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(deps, "DATA_ROOT", tmp_path)
    client = TestClient(app)

    upload = client.post(
        "/ingest/upload",
        files={"file": ("statement.pdf", _text_pdf_bytes("Statement Total 100.00"), "application/pdf")},
    )
    doc_id = upload.json()["doc_id"]

    scanned = client.post(f"/ingest/{doc_id}/scan", params={"ocr": "false"})
    assert scanned.status_code == 200
    assert scanned.json()["has_native_text"] is True


def test_ingest_scan_auto_uses_ocr_for_scanned_pdf(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(deps, "DATA_ROOT", tmp_path)

    def fake_ocr_pages(images, page_numbers=None):
        return [{"page": 1, "full_text": "Total 250.00", "boxes": []}]

    monkeypatch.setattr(document_scan_engine, "ocr_pages", fake_ocr_pages)

    client = TestClient(app)
    upload = client.post(
        "/ingest/upload",
        files={"file": ("scan.pdf", _scanned_pdf_bytes("Total 250.00"), "application/pdf")},
    )
    doc_id = upload.json()["doc_id"]

    scanned = client.post(f"/ingest/{doc_id}/scan", params={"ocr": "auto"})
    assert scanned.status_code == 200
    assert scanned.json()["pages_ocr_processed"] >= 1


def test_structure_stub_endpoint_returns_valid_schema(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(deps, "DATA_ROOT", tmp_path)
    client = TestClient(app)

    upload = client.post(
        "/ingest/upload",
        files={"file": ("invoice.pdf", _text_pdf_bytes("Invoice INV-001 Total 10.00"), "application/pdf")},
    )
    doc_id = upload.json()["doc_id"]
    client.post(f"/ingest/{doc_id}/scan", params={"ocr": "false"})

    structured = client.post(
        f"/ingest/{doc_id}/structure",
        params={"schema": "invoice", "mode": "stub"},
    )

    assert structured.status_code == 200
    assert structured.json()["invoice_no"]
    assert "line_items" in structured.json()


def test_get_ingest_and_artifact_endpoints(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(deps, "DATA_ROOT", tmp_path)
    client = TestClient(app)

    upload = client.post(
        "/ingest/upload",
        files={"file": ("invoice.pdf", _text_pdf_bytes("Invoice INV-001 Total 10.00"), "application/pdf")},
    )
    doc_id = upload.json()["doc_id"]
    client.post(f"/ingest/{doc_id}/scan", params={"ocr": "false"})

    doc_payload = client.get(f"/ingest/{doc_id}")
    assert doc_payload.status_code == 200
    assert "meta" in doc_payload.json()
    assert "summary" in doc_payload.json()

    artifact = client.get(f"/ingest/{doc_id}/artifact", params={"name": "summary"})
    assert artifact.status_code == 200
    assert artifact.json()["doc_id"] == doc_id
