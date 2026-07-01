from __future__ import annotations

from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, read_json, seed_v09_inputs
from trading_core.equity_v09_platform import audit_a_share_v09_platform, run_a_share_v09_daily_platform
from trading_core.equity_v100_prep import audit_a_share_v100_prep, build_a_share_v100_prep
from trading_core.equity_v100_prep import builder as v100_builder


def test_v100_prep_builds_ready_decision_and_audit(monkeypatch, tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(as_of_date=AS_OF_DATE, simulation_only=True, paths=paths)
    audit_a_share_v09_platform(as_of_date=AS_OF_DATE, paths=paths)
    monkeypatch.setattr(v100_builder, "_owner_daily_status", lambda *_args, **_kwargs: _owner_status())
    monkeypatch.setattr(v100_builder, "_verify_v098_platform", lambda *_args, **_kwargs: _platform_verified())
    monkeypatch.setattr(v100_builder, "_verify_cli_surface", lambda *_args, **_kwargs: _cli_verified())
    monkeypatch.setattr(v100_builder, "_load_or_run_full_pytest", lambda *_args, **_kwargs: _full_pytest_passed())

    result = build_a_share_v100_prep(as_of_date=AS_OF_DATE, paths=paths)
    assert result["overall_passed"] is True
    assert result["release_readiness_decision"] == "ready_for_v100_release"
    assert result["blocking_warning_count"] == 0
    assert result["owner_readiness_state"] == "blocked"
    assert result["broker_connected"] is False
    assert result["live_trading_ready"] is False

    warning = read_json(paths.data_dir / "equity_v100_prep" / "daily" / AS_OF_DATE / "v098_warning_classification.json")
    assert warning["warning_count"] == 2
    assert {item["warning_id"] for item in warning["classifications"]} == set(platform_json(paths, "v09_benchmark_attribution_result")["warnings"])
    assert all(item["blocking_for_v100"] is False for item in warning["classifications"])

    audit = audit_a_share_v100_prep(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert len(audit["warnings"]) == 2


def test_v100_prep_audit_fails_closed_on_boundary_change(monkeypatch, tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(as_of_date=AS_OF_DATE, simulation_only=True, paths=paths)
    audit_a_share_v09_platform(as_of_date=AS_OF_DATE, paths=paths)
    monkeypatch.setattr(v100_builder, "_owner_daily_status", lambda *_args, **_kwargs: _owner_status())
    monkeypatch.setattr(v100_builder, "_verify_v098_platform", lambda *_args, **_kwargs: _platform_verified())
    monkeypatch.setattr(v100_builder, "_verify_cli_surface", lambda *_args, **_kwargs: _cli_verified())
    monkeypatch.setattr(v100_builder, "_load_or_run_full_pytest", lambda *_args, **_kwargs: _full_pytest_passed())
    build_a_share_v100_prep(as_of_date=AS_OF_DATE, paths=paths)

    decision_path = paths.data_dir / "equity_v100_prep" / "daily" / AS_OF_DATE / "v100_release_readiness_decision.json"
    decision = read_json(decision_path)
    decision["broker_connected"] = True
    decision_path.write_text(__import__("json").dumps(decision, indent=2), encoding="utf-8")

    audit = audit_a_share_v100_prep(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is False
    assert "forbidden_boundary_true:broker_connected" in audit["blocking_reasons"]


def _platform_verified():
    return {
        "verification_id": "A-SHARE-V098-PLATFORM-VERIFICATION",
        "v098_platform_verified": True,
        "v098_audit_warning_count": 2,
        "blocking_reasons": [],
        "warnings": ["benchmark_data_missing_recorded_without_fabrication", "attribution_source_missing_using_simulated_summary"],
    }


def _full_pytest_passed():
    return {
        "result_id": "A-SHARE-V100-FULL-REGRESSION-RESULT",
        "target_version": "v1.0.0-prep-a-share-autonomous-simulation-platform-closeout",
        "as_of_date": AS_OF_DATE,
        "command": "python -m pytest",
        "returncode": 0,
        "full_pytest_run": True,
        "full_regression_passed": True,
        "total_passed": 10,
        "total_skipped": 1,
        "total_failed": 0,
        "total_errors": 0,
        "duration_seconds": 1.23,
        "blocking_reasons": [],
    }


def _cli_verified():
    return {
        "verification_id": "A-SHARE-V100-CLI-SURFACE-VERIFICATION",
        "cli_surface_verified": True,
        "blocking_reasons": [],
    }


def _owner_status():
    return {
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "readiness_score": 54,
        "minimum_owner_readiness_score": 75,
        "score_gap": 21,
        "order_preview_generated": False,
    }
