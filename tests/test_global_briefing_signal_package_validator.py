from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, fixture_path, make_paths, write_text
from trading_core.global_briefing.signal_package_validator import validate_global_briefing_signals


def test_valid_jsonl_passes(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = validate_global_briefing_signals(
        fixture_path(paths, "signals_valid.jsonl"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        paths=paths,
    )

    assert result["overall_passed"] is True
    assert result["valid_row_count"] == 4


def test_valid_json_passes(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = validate_global_briefing_signals(
        fixture_path(paths, "signals_valid.json"),
        start_date="2024-01-02",
        end_date="2024-01-03",
        paths=paths,
    )

    assert result["overall_passed"] is True
    assert result["input_format"] == "json"


def test_missing_input_blocks(tmp_path: Path) -> None:
    result = validate_global_briefing_signals("missing.jsonl", paths=make_paths(tmp_path))

    assert result["overall_passed"] is False
    assert any("input file missing" in item for item in result["blocking_reasons"])


def test_malformed_jsonl_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "bad.jsonl", "{not-json\n")

    result = validate_global_briefing_signals("bad.jsonl", paths=paths)

    assert result["overall_passed"] is False
    assert any("malformed JSONL" in item for item in result["blocking_reasons"])


def test_missing_required_field_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "missing_field.jsonl", '{"as_of_date":"2024-01-02"}\n')

    result = validate_global_briefing_signals("missing_field.jsonl", paths=paths)

    assert result["overall_passed"] is False
    assert any("missing required fields" in item for item in result["blocking_reasons"])


def test_invalid_as_of_date_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(
        paths.project_root / "bad_date.jsonl",
        '{"as_of_date":"2024/01/02","generated_at":"2024-01-02T06:00:00Z","region":"CN","signals":{},"source":"global_briefing","version":"v1"}\n',
    )

    result = validate_global_briefing_signals("bad_date.jsonl", paths=paths)

    assert result["overall_passed"] is False
    assert any("invalid as_of_date" in item for item in result["blocking_reasons"])


def test_invalid_generated_at_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(
        paths.project_root / "bad_generated.jsonl",
        '{"as_of_date":"2024-01-02","generated_at":"not-a-date","region":"CN","signals":{},"source":"global_briefing","version":"v1"}\n',
    )

    result = validate_global_briefing_signals("bad_generated.jsonl", paths=paths)

    assert result["overall_passed"] is False
    assert any("invalid generated_at" in item for item in result["blocking_reasons"])


def test_signals_not_object_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(
        paths.project_root / "signals_not_object.jsonl",
        '{"as_of_date":"2024-01-02","generated_at":"2024-01-02T06:00:00Z","region":"CN","signals":[],"source":"global_briefing","version":"v1"}\n',
    )

    result = validate_global_briefing_signals("signals_not_object.jsonl", paths=paths)

    assert result["overall_passed"] is False
    assert any("signals must be an object" in item for item in result["blocking_reasons"])


def test_future_generated_at_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = validate_global_briefing_signals(fixture_path(paths, "signals_future.jsonl"), paths=paths)

    assert result["overall_passed"] is False
    assert result["point_in_time"]["future_signal_rows"] == 1


def test_empty_package_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "empty.jsonl", "")

    result = validate_global_briefing_signals("empty.jsonl", paths=paths)

    assert result["overall_passed"] is False
    assert any("empty signal package" in item for item in result["blocking_reasons"])


def test_unknown_fields_warn(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = validate_global_briefing_signals(fixture_path(paths, "signals_valid.jsonl"), paths=paths)

    assert any("unknown fields" in item for item in result["warnings"])


def test_duplicate_date_does_not_crash(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = validate_global_briefing_signals(fixture_path(paths, "signals_valid.jsonl"), paths=paths)

    assert result["overall_passed"] is True
    assert result["duplicates"]["duplicate_as_of_dates"] == ["2024-01-05"]


def test_missing_dates_warn(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = validate_global_briefing_signals(
        fixture_path(paths, "signals_valid.jsonl"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        paths=paths,
    )

    assert "2024-01-04" in result["coverage"]["missing_dates"]
    assert result["warnings"]


def test_strict_missing_coverage_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = validate_global_briefing_signals(
        fixture_path(paths, "signals_valid.jsonl"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        strict=True,
        paths=paths,
    )

    assert result["overall_passed"] is False
    assert any("strict coverage failure" in item for item in result["blocking_reasons"])


def test_validation_markdown_contains_validation_only(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = validate_global_briefing_signals(fixture_path(paths, "signals_valid.jsonl"), paths=paths)

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "- validation only" in report


def test_validator_does_not_write_orders_trades_portfolio_accounts(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    validate_global_briefing_signals(fixture_path(paths, "signals_valid.jsonl"), paths=paths)

    assert_no_protected_paths(paths)


def test_validator_does_not_call_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["validate-global-briefing-signals", "--input", fixture_path(paths, "signals_valid.jsonl")]) == 0


def test_validator_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["validate-global-briefing-signals", "--input", fixture_path(paths, "signals_valid.jsonl")]) == 0
