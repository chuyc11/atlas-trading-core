"""End-to-end local real package isolated replay workflow."""

from __future__ import annotations

from typing import Any

from trading_core.global_briefing.historical_replay_runner import replay_global_briefing_history
from trading_core.global_briefing.real_package_coverage_audit import audit_global_briefing_package_coverage
from trading_core.global_briefing.real_package_normalizer import normalize_global_briefing_package
from trading_core.global_briefing.replay_bundle_builder import build_global_briefing_replay_bundle
from trading_core.global_briefing.replay_evaluation_report import build_global_briefing_replay_report
from trading_core.global_briefing.signal_schema import compact_date
from trading_core.global_briefing.signal_package_validator import validate_global_briefing_signals
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


def run_global_briefing_real_package_replay(
    input_path: str,
    prices_path: str,
    *,
    start_date: str,
    end_date: str,
    package_id: str | None = None,
    region: str | None = None,
    source: str | None = None,
    version: str | None = None,
    allow_carry_forward: bool = False,
    min_coverage: float = 0.80,
    execution_mode: str = "isolated",
    strict: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    workflow_id = f"GB-REAL-PACKAGE-WORKFLOW-{compact_date(start_date)}-{compact_date(end_date)}"
    warnings: list[str] = []
    blocking: list[str] = []
    outputs: dict[str, Any] = {"workflow_id": workflow_id, "input": input_path}

    normalization = normalize_global_briefing_package(input_path, package_id=package_id, region=region, source=source, version=version, strict=strict, paths=paths)
    outputs["normalization"] = normalization["json_path"]
    outputs["normalized_signals"] = normalization["output"]
    warnings.extend(normalization["warnings"])
    if not normalization["overall_passed"]:
        blocking.extend(normalization["blocking_reasons"])
        return _write_workflow_summary(outputs, start_date, end_date, warnings, blocking, paths)

    validation = validate_global_briefing_signals(normalization["output"], start_date=start_date, end_date=end_date, paths=paths)
    outputs["validation"] = validation["json_path"]
    warnings.extend(validation["warnings"])
    if not validation["overall_passed"]:
        blocking.extend(validation["blocking_reasons"])
        return _write_workflow_summary(outputs, start_date, end_date, warnings, blocking, paths)

    coverage = audit_global_briefing_package_coverage(
        normalization["output"],
        prices_path=prices_path,
        start_date=start_date,
        end_date=end_date,
        min_coverage=min_coverage,
        strict=strict,
        paths=paths,
    )
    outputs["coverage_audit"] = coverage["json_path"]
    warnings.extend(coverage["warnings"])
    if not coverage["overall_passed"]:
        blocking.extend(coverage["blocking_reasons"])
        return _write_workflow_summary(outputs, start_date, end_date, warnings, blocking, paths)

    try:
        bundle = build_global_briefing_replay_bundle(
            normalization["output"],
            prices_path,
            start_date=start_date,
            end_date=end_date,
            allow_carry_forward=allow_carry_forward,
            paths=paths,
        )
        outputs["bundle"] = bundle["json_path"]
        replay = replay_global_briefing_history(
            bundle["json_path"],
            prices_path,
            start_date=start_date,
            end_date=end_date,
            execution_mode=execution_mode,
            paths=paths,
        )
        outputs["replay"] = replay["json_path"]
        warnings.extend(replay["warnings"])
        evaluation = build_global_briefing_replay_report(
            replay["json_path"],
            bundle_path=bundle["json_path"],
            validation_path=validation["json_path"],
            paths=paths,
        )
        outputs["evaluation"] = evaluation["json_path"]
        warnings.extend(evaluation["warnings"])
        if evaluation["overall_status"] != "research_review_ready":
            blocking.extend(evaluation["blocking_reasons"])
    except ValueError as exc:
        blocking.append(str(exc))

    return _write_workflow_summary(outputs, start_date, end_date, warnings, blocking, paths)


def _write_workflow_summary(
    outputs: dict[str, Any],
    start_date: str,
    end_date: str,
    warnings: list[str],
    blocking: list[str],
    paths: ProjectPaths,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        **outputs,
        "start_date": start_date,
        "end_date": end_date,
        "overall_status": "research_review_ready" if not blocking else "needs_attention",
        "blocking_reasons": blocking,
        "warnings": warnings,
        "boundary": {
            "workflow_only": True,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "main_ledger_written": False,
            "isolated_replay_ledger_written": "replay" in outputs,
            "run_daily_called": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
            "network_access": False,
        },
    }
    json_path = paths.data_dir / "replays" / "global_briefing" / f"real_package_replay_workflow-{start_date}-{end_date}.json"
    report_path = paths.outputs_dir / "replays" / "global_briefing" / f"REAL_PACKAGE_REPLAY_WORKFLOW-{start_date}-{end_date}.md"
    write_json_markdown(json_path, payload, report_path, build_workflow_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_workflow_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Real Global Briefing Package Replay Workflow",
            "",
            "## Scope",
            "This workflow runs local historical global-briefing package replay in isolated mode.",
            "",
            "## Steps",
            "- normalize package",
            "- validate normalized signals",
            "- audit package coverage",
            "- build replay bundle",
            "- run isolated replay",
            "- generate replay evaluation",
            "",
            "## Outputs",
            *[f"- {key}: {value}" for key, value in payload.items() if key in {"normalized_signals", "validation", "coverage_audit", "bundle", "replay", "evaluation"}],
            "",
            "## Warnings",
            *([f"- {item}" for item in payload["warnings"]] if payload["warnings"] else ["- none"]),
            "",
            "## Boundary",
            "- local package only",
            "- no network access",
            "- isolated replay only",
            "- main ledger not written",
            "- run-daily not called",
            "- not forward dry-run validation",
            "- not live trading readiness",
            "- not strategy effectiveness proof",
            "",
        ]
    )
