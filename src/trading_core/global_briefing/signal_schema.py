"""Schema helpers for historical global-briefing macro signal packages."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


CONTRACT_ID = "GLOBAL-BRIEFING-SIGNAL-CONTRACT-V1"
CONTRACT_VERSION = "v1"
REQUIRED_FIELDS = ["as_of_date", "generated_at", "region", "signals", "source", "version"]
KNOWN_FIELDS = set(REQUIRED_FIELDS)
SUPPORTED_FORMATS = ["json", "jsonl"]
DEFAULT_DECISION_TIME = "09:00:00"
VALID_SIGNAL_VALUE_TYPES = (str, int, float, bool, type(None))
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class SignalPackage:
    input_path: Path
    input_format: str | None
    rows: list[dict[str, Any]]
    blocking_reasons: list[str]
    warnings: list[str]


def resolve_project_path(path: str | Path, paths: ProjectPaths) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    parts = [part.lower() for part in candidate.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / candidate
    return paths.project_root / candidate


def read_signal_package(path: str | Path, paths: ProjectPaths) -> SignalPackage:
    input_path = resolve_project_path(path, paths)
    blocking: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    if not input_path.exists():
        return SignalPackage(input_path, None, [], [f"input file missing: {input_path}"], [])

    suffix = input_path.suffix.lower()
    if suffix == ".jsonl":
        input_format = "jsonl"
        for line_number, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                blocking.append(f"malformed JSONL row {line_number}: {exc.msg}")
                continue
            if not isinstance(row, dict):
                blocking.append(f"malformed JSONL row {line_number}: row is not an object")
                continue
            rows.append(row)
    elif suffix == ".json":
        input_format = "json"
        try:
            payload = json.loads(input_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return SignalPackage(input_path, input_format, [], [f"malformed JSON: {exc.msg}"], [])
        if isinstance(payload, list):
            raw_rows = payload
        elif isinstance(payload, dict) and isinstance(payload.get("signals"), list):
            raw_rows = payload["signals"]
        elif isinstance(payload, dict) and all(field in payload for field in REQUIRED_FIELDS):
            raw_rows = [payload]
        else:
            raw_rows = []
            blocking.append("JSON package must contain a signals list or a single signal row")
        for index, row in enumerate(raw_rows, 1):
            if isinstance(row, dict):
                rows.append(row)
            else:
                blocking.append(f"malformed JSON signal row {index}: row is not an object")
    else:
        input_format = None
        blocking.append(f"unsupported signal package format: {input_path.suffix or '<none>'}")

    if not rows and not blocking:
        blocking.append("empty signal package")
    return SignalPackage(input_path, input_format, rows, blocking, warnings)


def validate_signal_row(
    row: dict[str, Any],
    row_number: int,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    decision_time: str = DEFAULT_DECISION_TIME,
    check_point_in_time: bool = True,
) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    blocking: list[str] = []
    warnings: list[str] = []
    clean = dict(row)

    missing = [field for field in REQUIRED_FIELDS if field not in row]
    if missing:
        blocking.append(f"row {row_number} missing required fields: {missing}")

    unknown = sorted(set(row) - KNOWN_FIELDS)
    if unknown:
        warnings.append(f"row {row_number} unknown fields ignored: {unknown}")

    as_of = row.get("as_of_date")
    as_of_date = parse_date(as_of)
    if as_of_date is None:
        blocking.append(f"row {row_number} invalid as_of_date: {as_of!r}")
    else:
        if start_date and as_of_date < date.fromisoformat(start_date):
            blocking.append(f"row {row_number} as_of_date before start-date: {as_of}")
        if end_date and as_of_date > date.fromisoformat(end_date):
            blocking.append(f"row {row_number} as_of_date after end-date: {as_of}")

    generated = row.get("generated_at")
    generated_dt, generated_warnings = parse_datetime(generated)
    warnings.extend(f"row {row_number} {item}" for item in generated_warnings)
    if generated_dt is None:
        blocking.append(f"row {row_number} invalid generated_at: {generated!r}")

    signals = row.get("signals")
    if not isinstance(signals, dict):
        blocking.append(f"row {row_number} signals must be an object")
    else:
        for key, value in signals.items():
            if not isinstance(key, str):
                blocking.append(f"row {row_number} signal key must be a string")
            if not isinstance(value, VALID_SIGNAL_VALUE_TYPES):
                blocking.append(f"row {row_number} signal value for {key!r} has unsupported type")

    for field in ["source", "version"]:
        value = row.get(field)
        if value is None or str(value).strip() == "":
            blocking.append(f"row {row_number} {field} must be explicit")

    if check_point_in_time and generated_dt is not None and as_of_date is not None:
        decision_dt = decision_timestamp(as_of_date.isoformat(), decision_time)
        if normalize_datetime(generated_dt) > decision_dt:
            blocking.append(
                f"row {row_number} future signal leakage: generated_at {generated} is after decision timestamp "
                f"{decision_dt.isoformat().replace('+00:00', 'Z')}"
            )

    if blocking:
        return None, blocking, warnings
    clean["as_of_date"] = as_of_date.isoformat() if as_of_date else str(as_of)
    clean["generated_at"] = str(generated)
    return clean, blocking, warnings


def parse_date(value: Any) -> date | None:
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_datetime(value: Any) -> tuple[datetime | None, list[str]]:
    warnings: list[str] = []
    if not isinstance(value, str) or not value.strip():
        return None, warnings
    text = value.strip()
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None, warnings
    if parsed.tzinfo is None:
        warnings.append("timezone ambiguity: generated_at has no timezone")
    return parsed, warnings


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def decision_timestamp(day: str, decision_time: str = DEFAULT_DECISION_TIME) -> datetime:
    parsed_time = time.fromisoformat(decision_time)
    return datetime.combine(date.fromisoformat(day), parsed_time, tzinfo=UTC)


def generated_sort_key(row: dict[str, Any]) -> datetime:
    parsed, _warnings = parse_datetime(row.get("generated_at"))
    return normalize_datetime(parsed or datetime.min.replace(tzinfo=UTC))


def calendar_dates(start_date: str, end_date: str) -> list[str]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        return []
    days: list[str] = []
    current = start
    from datetime import timedelta

    while current <= end:
        days.append(current.isoformat())
        current += timedelta(days=1)
    return days


def compact_date(date_text: str) -> str:
    return date_text.replace("-", "")
