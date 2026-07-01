"""Full pytest execution and result capture."""

from __future__ import annotations

import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_v090_rc.io import load_json
from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def run_full_pytest(*, as_of_date: str = DEFAULT_AS_OF_DATE, skip_full_pytest: bool = False, timeout_seconds: int | None = None) -> dict[str, Any]:
    if skip_full_pytest:
        return build_skipped_full_pytest_result(as_of_date=as_of_date)
    started = datetime.now(UTC)
    start = time.perf_counter()
    completed = subprocess.run([sys.executable, "-m", "pytest"], capture_output=True, text=True, timeout=timeout_seconds)
    finished = datetime.now(UTC)
    duration = time.perf_counter() - start
    return build_full_pytest_result(
        as_of_date=as_of_date,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        duration_seconds=duration,
        started_at=started.isoformat().replace("+00:00", "Z"),
        completed_at=finished.isoformat().replace("+00:00", "Z"),
    )


def load_reusable_full_pytest_result(path: Path, *, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any] | None:
    result = load_json(path)
    if not is_reusable_full_pytest_result(result, as_of_date=as_of_date):
        return None
    return result


def is_reusable_full_pytest_result(result: dict[str, Any], *, as_of_date: str = DEFAULT_AS_OF_DATE) -> bool:
    return (
        result.get("result_id") == "A-SHARE-V090-FULL-PYTEST-RESULT"
        and result.get("target_version") == TARGET_VERSION
        and result.get("as_of_date") == as_of_date
        and result.get("command") == "python -m pytest"
        and result.get("full_pytest_run") is True
        and result.get("full_pytest_skipped") is False
        and result.get("exit_code") == 0
        and result.get("overall_passed") is True
    )


def build_full_pytest_result(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    exit_code: int,
    stdout: str,
    stderr: str,
    duration_seconds: float,
    started_at: str | None = None,
    completed_at: str | None = None,
) -> dict[str, Any]:
    passed, failed, skipped = parse_pytest_counts(stdout)
    blocking = [] if exit_code == 0 else ["full_pytest_failed"]
    return {
        "result_id": "A-SHARE-V090-FULL-PYTEST-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "command": "python -m pytest",
        "started_at": started_at,
        "completed_at": completed_at,
        "full_pytest_run": True,
        "full_pytest_skipped": False,
        "result_source": "executed",
        "exit_code": exit_code,
        "passed_count": passed,
        "failed_count": failed,
        "skipped_count": skipped,
        "duration_seconds": round(duration_seconds, 3),
        "stdout_summary": _tail(stdout),
        "stderr_summary": _tail(stderr),
        "overall_passed": exit_code == 0,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def build_skipped_full_pytest_result(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V090-FULL-PYTEST-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "command": "python -m pytest",
        "started_at": None,
        "completed_at": None,
        "full_pytest_run": False,
        "full_pytest_skipped": True,
        "result_source": "skipped",
        "exit_code": None,
        "passed_count": 0,
        "failed_count": 0,
        "skipped_count": 0,
        "duration_seconds": 0,
        "stdout_summary": "full pytest skipped by --skip-full-pytest; build is not releasable",
        "stderr_summary": "",
        "overall_passed": False,
        "blocking_reasons": ["full_pytest_skipped_not_releasable"],
        "warnings": ["not_releasable"],
    }


def parse_pytest_counts(output: str) -> tuple[int, int, int]:
    summary = "\n".join(output.strip().splitlines()[-5:])
    passed = _count(summary, "passed")
    failed = _count(summary, "failed")
    skipped = _count(summary, "skipped")
    return passed, failed, skipped


def _count(text: str, label: str) -> int:
    match = re.search(rf"(\d+)\s+{label}", text)
    return int(match.group(1)) if match else 0


def _tail(text: str, line_count: int = 20) -> str:
    return "\n".join(text.strip().splitlines()[-line_count:])
