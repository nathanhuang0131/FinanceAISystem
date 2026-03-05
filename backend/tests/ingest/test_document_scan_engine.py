from __future__ import annotations

from pathlib import Path

import fitz
import pytest
from PIL import Image, ImageDraw

from backend.services import document_scan_engine
from backend.services.document_scan_engine import extract_native, scan


def make_text_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()


def make_scanned_pdf(path: Path, text: str) -> None:
    image = Image.new("RGB", (1600, 2200), "white")
    draw = ImageDraw.Draw(image)
    draw.text((100, 150), text, fill="black")

    img_path = path.with_suffix(".png")
    image.save(img_path)

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_image(page.rect, filename=str(img_path))
    doc.save(path)
    doc.close()


def test_extract_native_reads_text(tmp_path: Path):
    pdf_path = tmp_path / "text.pdf"
    make_text_pdf(pdf_path, "Invoice ABC-123")

    result = extract_native(pdf_path)

    assert result["page_count"] == 1
    assert "Invoice ABC-123" in result["pages"][0]["text"]


def test_scan_ocr_false_persists_native_artifacts(tmp_path: Path):
    pdf_path = tmp_path / "text.pdf"
    make_text_pdf(pdf_path, "Statement Total 100.00")
    extracted_dir = tmp_path / "extracted"

    summary = scan(
        pdf_path=pdf_path,
        doc_id="doc-1",
        filename="text.pdf",
        extracted_dir=extracted_dir,
        ocr_mode="false",
    )

    assert summary["has_native_text"] is True
    assert summary["has_ocr_text"] is False
    assert (extracted_dir / "summary.json").exists()
    assert (extracted_dir / "native_text.json").exists()
    assert (extracted_dir / "native_tables.json").exists()


def test_scan_auto_ocr_for_scanned_pdf(tmp_path: Path, monkeypatch):
    pdf_path = tmp_path / "scanned.pdf"
    make_scanned_pdf(pdf_path, "Total 250.00")
    extracted_dir = tmp_path / "extracted"

    def fake_ocr_pages(images, page_numbers=None):
        return [
            {
                "page": page_numbers[0] if page_numbers else 1,
                "full_text": "Total 250.00",
                "boxes": [],
            }
        ]

    monkeypatch.setattr(document_scan_engine, "ocr_pages", fake_ocr_pages)
    summary = scan(
        pdf_path=pdf_path,
        doc_id="doc-2",
        filename="scanned.pdf",
        extracted_dir=extracted_dir,
        ocr_mode="auto",
    )

    assert summary["pages_ocr_processed"] >= 1
    assert summary["has_ocr_text"] is True
