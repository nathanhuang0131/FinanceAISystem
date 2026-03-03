from __future__ import annotations

from pathlib import Path

from backend.services.ledger_engine import LedgerEngine
from backend.services.masterdata_engine import MasterDataEngine
from backend.services.statement_engine import StatementEngine
from backend.storage.bootstrap import init_data_dirs

DATA_ROOT = Path("data")


def get_data_root() -> Path:
    init_data_dirs(DATA_ROOT)
    return DATA_ROOT


def get_master_engine() -> MasterDataEngine:
    return MasterDataEngine(get_data_root())


def get_ledger_engine() -> LedgerEngine:
    return LedgerEngine(get_data_root())


def get_statement_engine() -> StatementEngine:
    return StatementEngine(get_data_root())
