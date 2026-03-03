from __future__ import annotations

from pathlib import Path

from backend.services.ledger_engine import LedgerEngine


def create_and_post_journal_workflow(base_path: Path, payload: dict[str, object]) -> dict[str, object]:
    engine = LedgerEngine(base_path)
    return engine.create_and_post_journal(
        date=str(payload.get("date", "")),
        memo=str(payload.get("memo", "")),
        reference=str(payload.get("reference", "")),
        lines=list(payload.get("lines", [])),
    )
