from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any
from collections.abc import Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "test-matrix"
TEST_DEFINITION = re.compile(rb"(?m)^\s*(?:async\s+)?def\s+test_")
SYSTEM_TEMP_ROOT = Path(tempfile.gettempdir()) / "trading-core-test-matrix"


@dataclass(frozen=True)
class WeightedTestFile:
    path: Path
    relative_path: str
    weight: int


def discover_test_files(project_root: Path = PROJECT_ROOT) -> list[WeightedTestFile]:
    tests_root = project_root / "tests"
    weighted: list[WeightedTestFile] = []
    for path in sorted(tests_root.glob("test_*.py")):
        payload = path.read_bytes()
        test_count = len(TEST_DEFINITION.findall(payload))
        size_units = max(1, (len(payload) + 4095) // 4096)
        weighted.append(
            WeightedTestFile(
                path=path,
                relative_path=path.relative_to(project_root).as_posix(),
                weight=max(1, test_count * 4 + size_units),
            )
        )
    return weighted


def partition_test_files(
    files: Sequence[WeightedTestFile],
    shard_count: int,
) -> list[list[WeightedTestFile]]:
    if shard_count < 1:
        raise ValueError("shard_count must be at least 1")
    if not files:
        return []
    shard_count = min(shard_count, len(files))
    shards: list[list[WeightedTestFile]] = [[] for _ in range(shard_count)]
    weights = [0] * shard_count
    for item in sorted(files, key=lambda value: (-value.weight, value.relative_path)):
        target = min(range(shard_count), key=lambda index: (weights[index], index))
        shards[target].append(item)
        weights[target] += item.weight
    for shard in shards:
        shard.sort(key=lambda value: value.relative_path)
    return shards


def parse_junit(path: Path) -> dict[str, int]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall(".//testsuite"))
    if not suites:
        raise ValueError(f"no testsuite found in {path}")
    if root.tag != "testsuite":
        direct = list(root.findall("testsuite"))
        if direct:
            suites = direct
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for suite in suites:
        for name in totals:
            totals[name] += int(float(suite.attrib.get(name, "0")))
    return totals


def shard_temp_path(
    project_root: Path,
    run_dir: Path,
    label: str,
) -> Path:
    project_key = hashlib.sha256(
        str(project_root.resolve()).encode("utf-8")
    ).hexdigest()[:12]
    candidate = (SYSTEM_TEMP_ROOT / project_key / run_dir.name / label).resolve()
    system_root = SYSTEM_TEMP_ROOT.resolve()
    if system_root not in candidate.parents:
        raise ValueError(f"shard temp path escapes system temp root: {candidate}")
    if project_root.resolve() in candidate.parents:
        raise ValueError(f"shard temp path must not be nested inside project root: {candidate}")
    return candidate


def _run_shard(
    *,
    shard_index: int,
    files: Sequence[WeightedTestFile],
    project_root: Path,
    run_dir: Path,
    timeout_seconds: float,
    extra_pytest_args: Sequence[str],
) -> dict[str, Any]:
    label = f"shard-{shard_index:02d}"
    log_path = run_dir / f"{label}.log"
    junit_path = run_dir / f"{label}.xml"
    temp_path = shard_temp_path(project_root, run_dir, label)
    temp_path.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pytest",
        *(item.relative_path for item in files),
        "--tb=short",
        f"--junitxml={junit_path}",
        f"--basetemp={temp_path}",
        *extra_pytest_args,
    ]
    started = time.monotonic()
    timed_out = False
    returncode: int | None = None
    error: str | None = None
    env = dict(os.environ)
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    source_path = str(project_root / "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        source_path
        if not existing_pythonpath
        else f"{source_path}{os.pathsep}{existing_pythonpath}"
    )
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        log.write(f"$ {' '.join(command)}\n\n")
        log.flush()
        try:
            completed = subprocess.run(
                command,
                cwd=project_root,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
            )
            returncode = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            error = f"timed out after {timeout_seconds:g} seconds"
            log.write(f"\n{error}\n")
        except OSError as exc:
            error = str(exc)
            log.write(f"\nrunner error: {error}\n")
    duration_seconds = round(time.monotonic() - started, 3)
    counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    if junit_path.is_file():
        try:
            counts = parse_junit(junit_path)
        except (ET.ParseError, OSError, ValueError) as exc:
            error = error or f"invalid JUnit report: {exc}"
    elif not timed_out:
        error = error or "pytest did not produce a JUnit report"
    passed = returncode == 0 and not timed_out and error is None
    return {
        "shard": shard_index,
        "status": "passed" if passed else ("timed_out" if timed_out else "failed"),
        "returncode": returncode,
        "duration_seconds": duration_seconds,
        "file_count": len(files),
        "estimated_weight": sum(item.weight for item in files),
        "counts": counts,
        "log": str(log_path),
        "junit": str(junit_path),
        "error": error,
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def run_matrix(
    *,
    project_root: Path = PROJECT_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    workers: int = 2,
    shard_count: int = 12,
    timeout_seconds: float = 900,
    extra_pytest_args: Sequence[str] = (),
) -> dict[str, Any]:
    files = discover_test_files(project_root)
    if not files:
        raise RuntimeError(f"no test files discovered under {project_root / 'tests'}")
    shards = partition_test_files(files, shard_count)
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_dir / run_id
    suffix = 1
    while run_dir.exists():
        run_dir = output_dir / f"{run_id}-{suffix}"
        suffix += 1
    run_dir.mkdir(parents=True)
    started = time.monotonic()
    results: list[dict[str, Any]] = []
    worker_count = min(workers, len(shards))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [
            executor.submit(
                _run_shard,
                shard_index=index,
                files=shard,
                project_root=project_root,
                run_dir=run_dir,
                timeout_seconds=timeout_seconds,
                extra_pytest_args=extra_pytest_args,
            )
            for index, shard in enumerate(shards, start=1)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["shard"])
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for result in results:
        for name in totals:
            totals[name] += int(result["counts"][name])
    passed = all(result["status"] == "passed" for result in results)
    summary = {
        "schema_version": 1,
        "status": "passed" if passed else "failed",
        "generated_at": datetime.now(UTC).isoformat(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "project_root": str(project_root),
        "test_file_count": len(files),
        "shard_count": len(shards),
        "worker_count": worker_count,
        "timeout_seconds_per_shard": timeout_seconds,
        "counts": totals,
        "shards": results,
    }
    atomic_write_json(run_dir / "summary.json", summary)
    atomic_write_json(output_dir / "latest.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the complete trading-core pytest suite in fail-closed shards."
    )
    parser.add_argument("--workers", type=int, default=min(2, os.cpu_count() or 1))
    parser.add_argument("--shards", type=int, default=12)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        help="Additional argument passed to every pytest shard.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.workers < 1 or args.shards < 1 or args.timeout <= 0:
        raise SystemExit("--workers, --shards, and --timeout must be positive")
    summary = run_matrix(
        output_dir=args.output_dir.resolve(),
        workers=args.workers,
        shard_count=args.shards,
        timeout_seconds=args.timeout,
        extra_pytest_args=args.pytest_arg,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
