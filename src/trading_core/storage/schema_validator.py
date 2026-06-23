"""Small schema validator for first-stage JSON records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_required_fields(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    missing = []
    for field in schema.get("required", []):
        if field not in record or record[field] is None:
            missing.append(field)
    return missing


def validate_record(record: dict[str, Any], schema_path: Path) -> None:
    schema = load_schema(schema_path)
    missing = validate_required_fields(record, schema)
    if missing:
        raise ValueError(f"Record missing required fields for {schema_path.name}: {missing}")
