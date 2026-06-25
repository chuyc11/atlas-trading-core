from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, real_fixture_path, write_json, write_text
from trading_core.global_briefing.real_package_normalizer import normalize_global_briefing_package
from trading_core.global_briefing.signal_package_validator import validate_global_briefing_signals


def test_jsonl_canonical_normalizes(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = normalize_global_briefing_package(real_fixture_path(paths, "real_package_canonical.jsonl"), paths=paths)

    assert result["overall_passed"] is True
    assert result["rows_out"] == 4


def test_json_package_normalizes(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_json(paths.project_root / "package.json", {"signals": [{"as_of_date": "2024-01-02", "generated_at": "2024-01-02T06:00:00Z", "region": "CN", "signals": {"risk_on": 0.1}, "source": "global_briefing", "version": "v1"}]})

    result = normalize_global_briefing_package("package.json", paths=paths)

    assert result["overall_passed"] is True
    assert result["rows_out"] == 1


def test_csv_package_and_aliases_normalize(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = normalize_global_briefing_package(real_fixture_path(paths, "real_package_aliases.csv"), package_id="GB-REAL-FIXTURE", source="global_briefing", version="v1", paths=paths)

    assert result["overall_passed"] is True
    assert result["field_mapping"]["date"] == "as_of_date"
    assert result["field_mapping"]["published_at"] == "generated_at"
    assert result["field_mapping"]["market"] == "region"


def test_signal_columns_enter_signals_object(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = normalize_global_briefing_package(real_fixture_path(paths, "real_package_aliases.csv"), package_id="GB-REAL-FIXTURE", source="global_briefing", version="v1", paths=paths)

    text = Path(result["output"]).read_text(encoding="utf-8")
    assert '"risk_on"' in text
    assert '"liquidity"' in text


def test_missing_generated_at_strict_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "missing_generated.csv", "date,market,risk_on\n2024-01-02,CN,0.1\n")

    result = normalize_global_briefing_package("missing_generated.csv", source="global_briefing", version="v1", strict=True, paths=paths)

    assert result["overall_passed"] is False
    assert any("missing generated_at" in item for item in result["blocking_reasons"])


def test_missing_generated_at_non_strict_warns(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "missing_generated.csv", "date,market,risk_on\n2024-01-02,CN,0.1\n")

    result = normalize_global_briefing_package("missing_generated.csv", source="global_briefing", version="v1", paths=paths)

    assert result["overall_passed"] is True
    assert any("generated_at missing" in item for item in result["warnings"])


def test_missing_region_source_version_can_be_filled_by_params(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "minimal.csv", "date,published_at,risk_on\n2024-01-02,2024-01-02T06:00:00Z,0.1\n")

    result = normalize_global_briefing_package("minimal.csv", region="CN", source="global_briefing", version="v1", paths=paths)

    assert result["overall_passed"] is True


def test_empty_signals_row_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "empty_signals.csv", "date,published_at,market\n2024-01-02,2024-01-02T06:00:00Z,CN\n")

    result = normalize_global_briefing_package("empty_signals.csv", source="global_briefing", version="v1", paths=paths)

    assert result["overall_passed"] is False
    assert any("signals empty" in item for item in result["blocking_reasons"])


def test_output_passes_signal_contract_validator(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = normalize_global_briefing_package(real_fixture_path(paths, "real_package_aliases.csv"), package_id="GB-REAL-FIXTURE", source="global_briefing", version="v1", paths=paths)

    validation = validate_global_briefing_signals(result["output"], start_date="2024-01-02", end_date="2024-01-08", paths=paths)

    assert validation["overall_passed"] is True


def test_normalizer_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = normalize_global_briefing_package(real_fixture_path(paths, "real_package_aliases.csv"), package_id="GB-REAL-FIXTURE", source="global_briefing", version="v1", paths=paths)

    assert result["boundary"]["network_access"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)


def test_normalizer_does_not_call_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["normalize-global-briefing-package", "--input", real_fixture_path(paths, "real_package_aliases.csv"), "--package-id", "GB-REAL-FIXTURE", "--source", "global_briefing", "--version", "v1"]) == 0


def test_normalizer_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["normalize-global-briefing-package", "--input", real_fixture_path(paths, "real_package_aliases.csv"), "--package-id", "GB-REAL-FIXTURE", "--source", "global_briefing", "--version", "v1"]) == 0
