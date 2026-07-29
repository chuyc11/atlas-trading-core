from __future__ import annotations

from pathlib import Path

from trading_core.testing.full_test_matrix import (
    WeightedTestFile,
    build_parser,
    parse_junit,
    partition_test_files,
    shard_temp_path,
)


def weighted(name: str, weight: int) -> WeightedTestFile:
    path = Path("tests") / name
    return WeightedTestFile(path=path, relative_path=path.as_posix(), weight=weight)


def test_partition_is_deterministic_and_balances_largest_files_first() -> None:
    files = [
        weighted("test_a.py", 10),
        weighted("test_b.py", 9),
        weighted("test_c.py", 8),
        weighted("test_d.py", 7),
        weighted("test_e.py", 6),
    ]

    first = partition_test_files(files, 2)
    second = partition_test_files(list(reversed(files)), 2)

    assert [[item.relative_path for item in shard] for shard in first] == [
        [item.relative_path for item in shard] for shard in second
    ]
    weights = [sum(item.weight for item in shard) for shard in first]
    assert max(weights) - min(weights) <= max(item.weight for item in files)


def test_partition_does_not_create_empty_shards() -> None:
    files = [weighted("test_a.py", 1), weighted("test_b.py", 1)]

    shards = partition_test_files(files, 8)

    assert len(shards) == 2
    assert all(shards)


def test_default_matrix_uses_small_shards_with_bounded_parallelism() -> None:
    args = build_parser().parse_args([])

    assert args.workers <= 2
    assert args.shards == 12
    assert args.timeout == 900


def test_shard_temp_path_stays_outside_project_checkout(tmp_path: Path) -> None:
    project_root = tmp_path / "checkout"
    run_dir = project_root / "outputs" / "test-matrix" / "run-1"

    target = shard_temp_path(project_root, run_dir, "shard-01")

    assert project_root.resolve() not in target.parents
    assert target.name == "shard-01"


def test_parse_junit_aggregates_direct_suites(tmp_path: Path) -> None:
    report = tmp_path / "report.xml"
    report.write_text(
        """
        <testsuites>
          <testsuite tests="3" failures="1" errors="0" skipped="1" />
          <testsuite tests="2" failures="0" errors="1" skipped="0" />
        </testsuites>
        """,
        encoding="utf-8",
    )

    assert parse_junit(report) == {
        "tests": 5,
        "failures": 1,
        "errors": 1,
        "skipped": 1,
    }
