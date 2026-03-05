from __future__ import annotations

from pathlib import Path

from backend.services.structure_engine import structure
from backend.storage.uploads import write_json


def _seed_extracted(tmp_path: Path, doc_id: str) -> None:
    extracted = tmp_path / doc_id / "extracted"
    extracted.mkdir(parents=True, exist_ok=True)
    write_json(
        extracted / "native_text.json",
        {
            "pages": [
                {
                    "page": 1,
                    "text": "Invoice INV-001 Supplier ACME Total 110.00 Tax 10.00 Subtotal 100.00",
                }
            ]
        },
    )
    write_json(extracted / "native_tables.json", {"pages": []})
    write_json(extracted / "ocr_text.json", {"pages": [{"page": 1, "full_text": "Receipt Total 20.00"}]})


def test_structure_stub_invoice_returns_valid_schema(tmp_path: Path):
    doc_id = "doc-structure"
    _seed_extracted(tmp_path, doc_id)

    result = structure(doc_id=doc_id, schema_name="invoice", mode="stub", base_dir=tmp_path)

    assert result["invoice_no"]
    assert result["total"] >= 0
    assert "line_items" in result


def test_structure_stub_bank_statement_returns_valid_schema(tmp_path: Path):
    doc_id = "doc-bank"
    _seed_extracted(tmp_path, doc_id)

    result = structure(doc_id=doc_id, schema_name="bank_statement", mode="stub", base_dir=tmp_path)

    assert result["bank"]
    assert "transactions" in result


def test_structure_stub_receipt_returns_valid_schema(tmp_path: Path):
    doc_id = "doc-receipt"
    _seed_extracted(tmp_path, doc_id)

    result = structure(doc_id=doc_id, schema_name="receipt", mode="stub", base_dir=tmp_path)

    assert result["merchant"]
    assert result["total"] >= 0
    assert "items" in result
