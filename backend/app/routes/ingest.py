from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from backend.app import deps
from backend.services.document_scan_engine import scan
from backend.services.structure_engine import structure
from backend.storage.uploads import get_doc_paths, read_json, save_original, write_json

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, object]:
    filename = file.filename or "upload.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    doc_id = uuid4().hex
    uploads_root = deps.get_data_root() / "uploads"
    original_path = save_original(file_bytes, filename, doc_id=doc_id, base_dir=uploads_root)
    paths = get_doc_paths(doc_id, base_dir=uploads_root)

    meta = {
        "doc_id": doc_id,
        "filename": filename,
        "size_bytes": len(file_bytes),
        "stored_path": str(original_path),
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
    }
    write_json(paths["meta_json"], meta)
    return meta


@router.post("/{doc_id}/scan")
def scan_doc(
    doc_id: str,
    ocr: Literal["auto", "true", "false"] = Query(default="auto"),
) -> dict[str, object]:
    uploads_root = deps.get_data_root() / "uploads"
    paths = get_doc_paths(doc_id, base_dir=uploads_root)

    if not paths["original_pdf"].exists():
        raise HTTPException(status_code=404, detail="Document not found")

    filename = f"{doc_id}.pdf"
    if paths["meta_json"].exists():
        filename = read_json(paths["meta_json"]).get("filename", filename)

    try:
        return scan(
            pdf_path=paths["original_pdf"],
            doc_id=doc_id,
            filename=filename,
            extracted_dir=paths["extracted_dir"],
            ocr_mode=ocr,
        )
    except RuntimeError as exc:
        msg = str(exc)
        if "install paddleocr/paddlepaddle" in msg or "model download" in msg.lower():
            raise HTTPException(status_code=500, detail=msg) from exc
        raise HTTPException(status_code=500, detail="Scan failed") from exc


@router.get("/{doc_id}")
def get_ingest_doc(doc_id: str) -> dict[str, object]:
    uploads_root = deps.get_data_root() / "uploads"
    paths = get_doc_paths(doc_id, base_dir=uploads_root)

    if not paths["meta_json"].exists():
        raise HTTPException(status_code=404, detail="Document not found")

    payload: dict[str, object] = {"meta": read_json(paths["meta_json"])}
    if paths["summary_json"].exists():
        payload["summary"] = read_json(paths["summary_json"])
    return payload


@router.get("/{doc_id}/artifact")
def get_artifact(
    doc_id: str,
    name: Literal["native_text", "native_tables", "ocr_text", "summary"],
) -> dict[str, object]:
    uploads_root = deps.get_data_root() / "uploads"
    paths = get_doc_paths(doc_id, base_dir=uploads_root)

    lookup = {
        "native_text": paths["native_text_json"],
        "native_tables": paths["native_tables_json"],
        "ocr_text": paths["ocr_text_json"],
        "summary": paths["summary_json"],
    }
    target = lookup[name]
    if not target.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")

    return read_json(target)


@router.post("/{doc_id}/structure")
def structure_doc(
    doc_id: str,
    schema: Literal["invoice", "bank_statement", "receipt"],
    mode: Literal["stub", "llm"] = Query(default="stub"),
) -> dict[str, object]:
    uploads_root = deps.get_data_root() / "uploads"
    paths = get_doc_paths(doc_id, base_dir=uploads_root)

    if not paths["meta_json"].exists():
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        payload = structure(doc_id=doc_id, schema_name=schema, mode=mode, base_dir=uploads_root)
    except ValueError as exc:
        detail = str(exc)
        status = 422 if "validation" in detail.lower() else 400
        raise HTTPException(status_code=status, detail=detail) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    write_json(paths["extracted_dir"] / f"structured_{schema}.json", payload)
    return payload
