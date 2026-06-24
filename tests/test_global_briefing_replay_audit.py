from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import fixture_path, make_paths, write_json
from trading_core.global_briefing.historical_replay_runner import replay_global_briefing_history
from trading_core.global_briefing.replay_audit import RELEASE_CANDIDATE, audit_global_briefing_replay
from trading_core.global_briefing.replay_bundle_builder import build_global_briefing_replay_bundle
from trading_core.global_briefing.replay_evaluation_report import build_global_briefing_replay_report
from trading_core.global_briefing.signal_contract import build_signal_contract
from trading_core.global_briefing.signal_package_validator import validate_global_briefing_signals


def _artifacts(paths) -> dict:
    contract = build_signal_contract(paths)
    validation = validate_global_briefing_signals(
        fixture_path(paths, "signals_valid.jsonl"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        paths=paths,
    )
    bundle = build_global_briefing_replay_bundle(
        fixture_path(paths, "signals_valid.jsonl"),
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        allow_carry_forward=True,
        paths=paths,
    )
    replay = replay_global_briefing_history(
        bundle["json_path"],
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        paths=paths,
    )
    evaluation = build_global_briefing_replay_report(
        replay["json_path"],
        bundle_path=bundle["json_path"],
        validation_path=validation["json_path"],
        paths=paths,
    )
    return {
        "contract": contract,
        "validation": validation,
        "bundle": bundle,
        "replay": replay,
        "evaluation": evaluation,
    }


def test_audit_json_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _artifacts(paths)

    result = audit_global_briefing_replay(paths=paths)

    assert Path(result["json_path"]).exists()
    assert result["overall_passed"] is True


def test_audit_markdown_generated(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _artifacts(paths)

    result = audit_global_briefing_replay(paths=paths)

    assert "# Global Briefing Replay Audit" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_missing_contract_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    Path(artifacts["contract"]["json_path"]).unlink()

    result = audit_global_briefing_replay(paths=paths)

    assert result["overall_passed"] is False
    assert any("contract" in item for item in result["blocking_reasons"])


def test_validation_failed_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["validation"]["overall_passed"] = False
    write_json(Path(artifacts["validation"]["json_path"]), artifacts["validation"])

    result = audit_global_briefing_replay(paths=paths)

    assert any("signal_validation" in item for item in result["blocking_reasons"])


def test_future_signal_used_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["bundle"]["point_in_time"]["future_signal_used"] = True
    write_json(Path(artifacts["bundle"]["json_path"]), artifacts["bundle"])

    result = audit_global_briefing_replay(paths=paths)

    assert any("replay_bundle" in item for item in result["blocking_reasons"])


def test_replay_isolated_false_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["replay"]["isolated"] = False
    write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_global_briefing_replay(paths=paths)

    assert any("historical_replay" in item for item in result["blocking_reasons"])


def test_main_ledger_written_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["replay"]["boundary"]["main_ledger_written"] = True
    write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_global_briefing_replay(paths=paths)

    assert any("main_ledger_written" in item for item in result["blocking_reasons"])


def test_run_daily_called_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["replay"]["boundary"]["run_daily_called"] = True
    write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_global_briefing_replay(paths=paths)

    assert any("run_daily_called" in item for item in result["blocking_reasons"])


def test_labels_ml_experiments_true_block(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    for key in ["labels_used", "ml_shadow_used", "experiments_used"]:
        artifacts["replay"]["boundary"][key] = True
    write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_global_briefing_replay(paths=paths)

    assert any("labels_used" in item for item in result["blocking_reasons"])
    assert any("ml_shadow_used" in item for item in result["blocking_reasons"])
    assert any("experiments_used" in item for item in result["blocking_reasons"])


def test_promotion_triggered_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["replay"]["boundary"]["promotion_triggered"] = True
    write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_global_briefing_replay(paths=paths)

    assert any("promotion_triggered" in item for item in result["blocking_reasons"])


def test_evaluation_strategy_effectiveness_proven_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["evaluation"]["boundary"]["strategy_effectiveness_proven"] = True
    write_json(Path(artifacts["evaluation"]["json_path"]), artifacts["evaluation"])

    result = audit_global_briefing_replay(paths=paths)

    assert any("evaluation" in item for item in result["blocking_reasons"])


def test_forbidden_wording_live_trading_ready_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    Path(artifacts["contract"]["report_path"]).write_text("live trading ready\n", encoding="utf-8")

    result = audit_global_briefing_replay(paths=paths)

    assert any("wording" in item for item in result["blocking_reasons"])


def test_protected_path_snapshot_unchanged(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _artifacts(paths)

    result = audit_global_briefing_replay(paths=paths)

    assert result["sections"]["protected_path_snapshot"]["passed"] is True
    assert result["sections"]["protected_path_snapshot"]["modified_paths"] == []


def test_report_contains_not_forward_dry_run_validation(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _artifacts(paths)
    report = Path(audit_global_briefing_replay(paths=paths)["report_path"]).read_text(encoding="utf-8")

    assert "This is not forward dry-run validation." in report


def test_report_contains_not_live_trading_readiness(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _artifacts(paths)
    report = Path(audit_global_briefing_replay(paths=paths)["report_path"]).read_text(encoding="utf-8")

    assert "This is not live trading readiness." in report


def test_report_contains_does_not_prove_strategy_effectiveness(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _artifacts(paths)
    report = Path(audit_global_briefing_replay(paths=paths)["report_path"]).read_text(encoding="utf-8")

    assert "This does not prove strategy effectiveness." in report


def test_overall_passed_recommends_v054_tag(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _artifacts(paths)
    result = audit_global_briefing_replay(paths=paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is True
    assert RELEASE_CANDIDATE in report


def test_overall_failed_does_not_recommend_tag(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    Path(artifacts["contract"]["json_path"]).unlink()
    result = audit_global_briefing_replay(paths=paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is False
    assert RELEASE_CANDIDATE not in report


def test_audit_does_not_call_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _artifacts(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["audit-global-briefing-replay"]) == 0


def test_audit_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _artifacts(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["audit-global-briefing-replay"]) == 0
