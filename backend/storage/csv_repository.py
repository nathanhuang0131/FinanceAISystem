from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


class CsvTable:
    def __init__(self, path: Path, headers: list[str]) -> None:
        self.path = Path(path)
        self.headers = headers
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=self.headers)
                writer.writeheader()

    def read_all(self) -> list[dict[str, str]]:
        with self.path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return [dict(row) for row in reader]

    def append(self, row: dict[str, object]) -> None:
        payload = {header: str(row.get(header, "")) for header in self.headers}
        with self.path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.headers)
            writer.writerow(payload)

    def write_all(self, rows: Iterable[dict[str, object]]) -> None:
        with self.path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.headers)
            writer.writeheader()
            for row in rows:
                payload = {header: str(row.get(header, "")) for header in self.headers}
                writer.writerow(payload)

    def upsert(self, key_field: str, row: dict[str, object]) -> dict[str, str]:
        rows = self.read_all()
        key_value = str(row.get(key_field, ""))
        replacement = {header: str(row.get(header, "")) for header in self.headers}
        replaced = False
        for index, existing in enumerate(rows):
            if existing.get(key_field) == key_value:
                rows[index] = replacement
                replaced = True
                break
        if not replaced:
            rows.append(replacement)
        self.write_all(rows)
        return replacement

    def find_one(self, key_field: str, key_value: str) -> dict[str, str] | None:
        for row in self.read_all():
            if row.get(key_field) == str(key_value):
                return row
        return None
