from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import fitz
import pdfplumber
from pypdf import PdfReader
from PIL import Image

from backend.storage.uploads import write_json


def extract_native(pdf_path: Path) -> dict[str, Any]:
    reader = PdfReader(str(pdf_path))
    native_pages: list[dict[str, Any]] = []

    with pdfplumber.open(str(pdf_path)) as plumber_pdf:
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            tables: list[Any] = []
            try:
                plumber_page = plumber_pdf.pages[index - 1]
                extracted_tables = plumber_page.extract_tables() or []
                tables = [table for table in extracted_tables if table]
            except Exception:
                tables = []
            native_pages.append({"page": index, "text": text, "tables": tables})

    return {"page_count": len(native_pages), "pages": native_pages}


def render_pages(pdf_path: Path, dpi: int = 200, zoom: float = 2.0) -> list[Image.Image]:
    scale = max(zoom, dpi / 72.0)
    matrix = fitz.Matrix(scale, scale)
    doc = fitz.open(str(pdf_path))
    images: list[Image.Image] = []

    try:
        for page in doc:
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            image = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
            images.append(image)
    finally:
        doc.close()

    return images


def _build_ocr_engine():
    try:
        from paddleocr import PaddleOCR
    except Exception as exc:
        raise RuntimeError("install paddleocr/paddlepaddle") from exc

    try:
        return PaddleOCR(use_angle_cls=True, lang="en")
    except Exception as exc:
        raise RuntimeError(
            "PaddleOCR model download failed. Check README OCR setup and network access."
        ) from exc


def ocr_pages(images: list[Image.Image], page_numbers: list[int] | None = None) -> list[dict[str, Any]]:
    ocr = _build_ocr_engine()
    results: list[dict[str, Any]] = []

    for idx, image in enumerate(images):
        page_no = page_numbers[idx] if page_numbers else idx + 1
        try:
            page_raw = ocr.ocr(image, cls=True)
        except Exception as exc:
            raise RuntimeError(
                "PaddleOCR model download failed. Check README OCR setup and network access."
            ) from exc

        boxes: list[dict[str, Any]] = []
        lines: list[str] = []

        if isinstance(page_raw, list) and page_raw:
            candidates = page_raw[0] if isinstance(page_raw[0], list) else page_raw
            for entry in candidates:
                if not isinstance(entry, (list, tuple)) or len(entry) < 2:
                    continue
                box = entry[0]
                text_data = entry[1]
                if isinstance(text_data, (list, tuple)) and text_data:
                    text = str(text_data[0])
                    confidence = float(text_data[1]) if len(text_data) > 1 else None
                else:
                    text = str(text_data)
                    confidence = None
                lines.append(text)
                boxes.append({"box": box, "text": text, "confidence": confidence})

        results.append({"page": page_no, "full_text": "\n".join(lines).strip(), "boxes": boxes})

    return results


def scan(
    pdf_path: Path,
    doc_id: str,
    filename: str,
    extracted_dir: Path,
    ocr_mode: str = "auto",
    min_native_chars: int = 50,
) -> dict[str, Any]:
    extracted_dir.mkdir(parents=True, exist_ok=True)
    native = extract_native(pdf_path)

    native_text_payload = {
        "page_count": native["page_count"],
        "pages": [{"page": p["page"], "text": p["text"]} for p in native["pages"]],
    }
    native_tables_payload = {
        "page_count": native["page_count"],
        "pages": [{"page": p["page"], "tables": p["tables"]} for p in native["pages"]],
    }
    write_json(extracted_dir / "native_text.json", native_text_payload)
    write_json(extracted_dir / "native_tables.json", native_tables_payload)

    mode = str(ocr_mode).lower()
    if mode not in {"auto", "true", "false"}:
        raise ValueError("ocr_mode must be one of: auto, true, false")

    page_indexes_to_ocr: list[int] = []
    if mode == "true":
        page_indexes_to_ocr = list(range(native["page_count"]))
    elif mode == "auto":
        for i, page in enumerate(native["pages"]):
            text_len = len((page["text"] or "").strip())
            if text_len < min_native_chars:
                page_indexes_to_ocr.append(i)

    ocr_output: list[dict[str, Any]] = []
    if page_indexes_to_ocr:
        images = render_pages(pdf_path)
        selected_images = [images[i] for i in page_indexes_to_ocr]
        selected_pages = [i + 1 for i in page_indexes_to_ocr]
        ocr_output = ocr_pages(selected_images, selected_pages)
        write_json(extracted_dir / "ocr_text.json", {"pages": [{"page": p["page"], "full_text": p["full_text"]} for p in ocr_output]})
        write_json(extracted_dir / "ocr_boxes.json", {"pages": [{"page": p["page"], "boxes": p["boxes"]} for p in ocr_output]})

    native_text_all = "\n".join((p["text"] or "").strip() for p in native["pages"]).strip()
    ocr_text_all = "\n".join((p.get("full_text") or "").strip() for p in ocr_output).strip()
    has_tables = any(bool(p["tables"]) for p in native["pages"])

    preview = (native_text_all + "\n" + ocr_text_all).strip()[:300]
    summary = {
        "doc_id": doc_id,
        "filename": filename,
        "page_count": native["page_count"],
        "has_native_text": bool(native_text_all),
        "has_tables": has_tables,
        "has_ocr_text": bool(ocr_text_all),
        "ocr_mode_used": mode,
        "pages_ocr_processed": len(page_indexes_to_ocr),
        "preview_snippet": preview,
    }
    write_json(extracted_dir / "summary.json", summary)
    return summary
