from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_UPLOADS_DIR = Path("data") / "uploads"


def create_doc_dir(doc_id: str, base_dir: Path | None = None) -> dict[str, Path]:
    uploads_root = (base_dir or DEFAULT_UPLOADS_DIR)
    doc_dir = uploads_root / doc_id
    extracted_dir = doc_dir / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    return {"uploads_root": uploads_root, "doc_dir": doc_dir, "extracted_dir": extracted_dir}


def save_original(file_bytes: bytes, filename: str, doc_id: str, base_dir: Path | None = None) -> Path:
    paths = create_doc_dir(doc_id, base_dir=base_dir)
    original_pdf = paths["doc_dir"] / "original.pdf"
    original_pdf.write_bytes(file_bytes)
    return original_pdf


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=True), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def get_doc_paths(doc_id: str, base_dir: Path | None = None) -> dict[str, Path]:
    uploads_root = (base_dir or DEFAULT_UPLOADS_DIR)
    doc_dir = uploads_root / doc_id
    extracted_dir = doc_dir / "extracted"
    return {
        "uploads_root": uploads_root,
        "doc_dir": doc_dir,
        "original_pdf": doc_dir / "original.pdf",
        "meta_json": doc_dir / "meta.json",
        "extracted_dir": extracted_dir,
        "summary_json": extracted_dir / "summary.json",
        "native_text_json": extracted_dir / "native_text.json",
        "native_tables_json": extracted_dir / "native_tables.json",
        "ocr_text_json": extracted_dir / "ocr_text.json",
        "ocr_boxes_json": extracted_dir / "ocr_boxes.json",
    }
