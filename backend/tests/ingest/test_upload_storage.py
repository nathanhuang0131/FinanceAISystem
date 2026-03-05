from pathlib import Path

from backend.storage.uploads import (
    create_doc_dir,
    get_doc_paths,
    read_json,
    save_original,
    write_json,
)


def test_storage_contract_roundtrip(tmp_path: Path):
    doc_id = "abc123"
    paths = create_doc_dir(doc_id, base_dir=tmp_path)

    assert paths["doc_dir"] == tmp_path / doc_id
    assert paths["extracted_dir"] == tmp_path / doc_id / "extracted"

    saved = save_original(b"%PDF-1.4", "x.pdf", doc_id=doc_id, base_dir=tmp_path)
    assert saved.exists()
    assert saved.name == "original.pdf"

    meta_path = tmp_path / doc_id / "meta.json"
    write_json(meta_path, {"doc_id": doc_id, "filename": "x.pdf"})
    assert read_json(meta_path)["filename"] == "x.pdf"

    resolved = get_doc_paths(doc_id, base_dir=tmp_path)
    assert resolved["original_pdf"] == tmp_path / doc_id / "original.pdf"
    assert resolved["summary_json"] == tmp_path / doc_id / "extracted" / "summary.json"
