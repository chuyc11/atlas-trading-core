"""Fixed-structure subprocess commands used by isolated research workflows."""

from __future__ import annotations

import subprocess
import sys
from datetime import date


_CURRENT_DAY_WORKFLOW_TAIL = (
    "-m",
    "trading_core.cli",
    "run-and-audit-a-share-current-day-research",
    "--as-of-date",
    "{as_of_date}",
    "--mode",
    "run_research_from_existing_refresh",
    "--workflow-mode",
    "build_from_existing_data",
)


def normalize_iso_date(value: str) -> str:
    """Return a canonical YYYY-MM-DD date or fail closed."""
    if not isinstance(value, str):
        raise ValueError("as_of_date must be a string in YYYY-MM-DD format")
    try:
        normalized = date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError("as_of_date must be a valid date in YYYY-MM-DD format") from exc
    if value != normalized:
        raise ValueError("as_of_date must use canonical YYYY-MM-DD format")
    return normalized


def current_day_workflow_argv(as_of_date: str, *, executable: bool = False) -> list[str]:
    """Build the allowlisted argv; no caller-controlled command fragments are accepted."""
    normalized = normalize_iso_date(as_of_date)
    program = sys.executable if executable else "python"
    return [program, *(part.format(as_of_date=normalized) for part in _CURRENT_DAY_WORKFLOW_TAIL)]


def current_day_workflow_display(as_of_date: str) -> str:
    """Create a human-readable command while execution continues to use argv."""
    return subprocess.list2cmdline(current_day_workflow_argv(as_of_date))
