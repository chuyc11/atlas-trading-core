"""CLI inventory for Trading Core."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


CORE_NO_LEDGER = ["orders", "trades", "portfolio", "accounts"]


def _record(command: str, category: str, purpose: str, writes_to: list[str], safety: list[str]) -> dict[str, Any]:
    return {
        "command": command,
        "category": category,
        "purpose": purpose,
        "writes_to": writes_to,
        "does_not_write_to": CORE_NO_LEDGER,
        "safety": safety,
    }


COMMANDS: list[dict[str, Any]] = [
    _record("init", "core / daily", "Initialize project directories", ["data", "outputs"], ["setup_only"]),
    _record("load-macro", "core / daily", "Load macro signals", ["stdout"], ["read_only"]),
    _record("generate-signals", "core / daily", "Planned virtual signal generation", ["data/signals"], ["virtual_only"]),
    _record("generate-orders", "core / daily", "Planned virtual order generation", ["data/orders"], ["virtual_only", "no_broker"]),
    _record("execute", "core / daily", "Planned virtual execution", ["data/trades"], ["virtual_only", "no_broker"]),
    _record("mark", "core / daily", "Planned mark-to-market", ["data/portfolios"], ["virtual_only"]),
    _record("benchmark", "core / daily", "Planned benchmark generation", ["data/benchmarks"], ["research_only"]),
    _record("attribution", "core / daily", "Planned attribution generation", ["data/attribution"], ["research_only"]),
    _record("score-signals", "evolution", "Planned signal scoring", ["data/evolution"], ["research_only"]),
    _record("classify-mistakes", "evolution", "Planned mistake classification", ["data/evolution"], ["diagnostic_only"]),
    _record("score-strategies", "evolution", "Planned strategy scoring", ["data/evolution"], ["not_promotion"]),
    _record("update-rule-memory", "evolution", "Planned rule memory update", ["data/evolution"], ["research_only"]),
    _record("update-experiment-queue", "evolution", "Planned experiment queue update", ["data/evolution"], ["research_only"]),
    _record("run-evolution", "evolution", "Planned evolution workflow", ["data/evolution"], ["no_auto_promotion"]),
    _record("report", "core / daily", "Planned daily report", ["outputs/daily"], ["report_only"]),
    _record("run-daily", "core / daily", "Run virtual daily workflow", ["data/signals", "data/orders", "data/trades", "data/portfolios", "outputs/daily"], ["virtual_only", "no_broker", "not_live"]),
    _record("health", "health / consistency", "Load or generate runtime health", ["data/runtime"], ["virtual_only"]),
    _record("export-summary", "reports", "Export virtual trading summary", ["data/exports"], ["virtual_summary"]),
    _record("backtest", "backtest / replay", "Run historical backtest", ["data/backtests", "outputs/backtests"], ["historical_only"]),
    _record("walk-forward", "backtest / replay", "Run walk-forward summary", ["stdout"], ["research_only"]),
    _record("summarize-health", "health / consistency", "Summarize runtime health", ["stdout"], ["read_only"]),
    _record("import-prices", "data acquisition / validation", "Import historical prices", ["data/raw"], ["data_only"]),
    _record("admission", "audits", "Run admission research check", ["stdout"], ["not_auto_promotion"]),
    _record("acceptance-report", "reports", "Write acceptance report materials", ["outputs"], ["documentation_only"]),
    _record("leaderboard", "reports", "Build strategy leaderboard", ["outputs/strategy-leaderboard"], ["research_only"]),
    _record("validate-data-package", "data acquisition / validation", "Validate data package", ["outputs/validation"], ["validation_only"]),
    _record("run-backtest-batch", "backtest / replay", "Run batch backtests", ["data/backtests", "outputs/backtests"], ["historical_only"]),
    _record("audit-dry-run", "backtest / replay", "Audit dry-run range", ["outputs/audit"], ["audit_only"]),
    _record("check-consistency", "health / consistency", "Check daily consistency", ["outputs/consistency"], ["audit_only"]),
    _record("check-consistency-range", "health / consistency", "Check range consistency", ["outputs/consistency"], ["audit_only"]),
    _record("fetch-prices", "data acquisition / validation", "Fetch price data", ["configured output"], ["data_only"]),
    _record("merge-price-data", "data acquisition / validation", "Merge price datasets", ["configured output"], ["data_only"]),
    _record("real-data-validation-report", "data acquisition / validation", "Build real data validation report", ["outputs/validation"], ["report_only"]),
    _record("dry-run-validation-report", "backtest / replay", "Build dry-run validation report", ["outputs/validation"], ["not_forward_proof"]),
    _record("replay-dry-run", "backtest / replay", "Replay historical dry-run", ["data/replays", "outputs/replays"], ["historical_only"]),
    _record("replay-last-trading-days", "backtest / replay", "Replay last trading days", ["data/replays", "outputs/replays"], ["historical_only"]),
    _record("build-features", "feature / label", "Build feature matrix", ["data/features", "outputs/features"], ["research_only"]),
    _record("build-labels", "feature / label", "Build label matrix", ["data/labels", "outputs/labels"], ["not_run_daily_input"]),
    _record("build-ml-dataset", "feature / label", "Build ML walk-forward dataset", ["data/ml", "outputs/ml"], ["research_only"]),
    _record("train-ml-shadow", "ml shadow", "Train shadow model", ["data/ml", "outputs/ml"], ["shadow_only"]),
    _record("predict-ml-shadow", "ml shadow", "Generate shadow predictions", ["data/ml"], ["shadow_only"]),
    _record("generate-ml-shadow-signals", "ml shadow", "Generate shadow signals", ["data/shadow", "outputs/shadow"], ["shadow_output_is_not_order"]),
    _record("ml-shadow-leaderboard", "ml shadow", "Build shadow leaderboard", ["data/shadow", "outputs/shadow"], ["not_promotion"]),
    _record("ml-shadow-report", "ml shadow", "Build shadow report", ["outputs/shadow"], ["report_only"]),
    _record("register-experiment", "experiments", "Register experiment", ["data/experiments"], ["registry_only"]),
    _record("list-experiments", "experiments", "List experiments", ["stdout"], ["read_only"]),
    _record("show-experiment", "experiments", "Show experiment", ["stdout"], ["read_only"]),
    _record("run-parameter-sweep", "experiments", "Run parameter sweep", ["data/experiments", "outputs/experiments"], ["shadow_only"]),
    _record("experiment-dashboard", "experiments", "Build experiment dashboard", ["data/experiments", "outputs/experiments"], ["read_only_summary"]),
    _record("simulate-promotion", "experiments", "Simulate promotion", ["data/experiments", "outputs/experiments"], ["simulation_is_not_promotion"]),
    _record("compare-strategies", "experiments", "Compare strategies", ["data/experiments", "outputs/experiments"], ["comparison_only"]),
    _record("update-mistake-patterns", "experiments", "Update mistake pattern library", ["data/experiments", "outputs/experiments"], ["diagnostic_only"]),
    _record("audit-experiment-system", "audits", "Audit experiment system", ["data/experiments", "outputs/audit"], ["audit_only"]),
    _record("weekly-research-report", "reports", "Generate weekly research report", ["data/reports", "outputs/reports"], ["research_only", "not_an_admission_gate"]),
    _record("monthly-research-report", "reports", "Generate monthly research report", ["data/reports", "outputs/reports"], ["research_only", "not_an_admission_gate"]),
    _record("system-dashboard", "reports", "Generate system dashboard", ["data/system", "outputs/system"], ["status_only"]),
    _record("project-status-report", "reports", "Generate project status report", ["data/system", "outputs/system"], ["governance_only"]),
    _record("run-research-pipeline", "reports", "Run research reporting pipeline", ["data/reports", "data/system", "outputs/reports", "outputs/system"], ["research_only", "not_run_daily"]),
    _record("audit-reporting-system", "audits", "Audit reporting system", ["data/system", "outputs/audit"], ["audit_only"]),
    _record("cli-inventory", "audits", "Generate CLI inventory", ["data/system", "outputs/system"], ["inventory_only", "not_run_daily"]),
    _record("artifact-inventory", "audits", "Generate artifact inventory", ["data/system", "outputs/system"], ["inventory_only", "not_run_daily"]),
    _record("system-smoke-test", "audits", "Run non-trading system smoke test", ["data/system", "outputs/system"], ["smoke_only", "not_run_daily"]),
    _record("boundary-regression-audit", "audits", "Audit boundary regressions", ["data/system", "outputs/audit"], ["audit_only", "not_run_daily"]),
    _record("system-integrity-audit", "audits", "Audit system integrity release candidate", ["data/system", "outputs/audit"], ["release_audit_only", "not_run_daily"]),
    _record("final-handoff-review", "reports", "Generate final human handoff review", ["data/system", "outputs/system"], ["handoff_only", "not_run_daily"]),
    _record("report-index", "reports", "Generate human report index", ["data/system", "outputs/system"], ["index_only", "not_run_daily"]),
    _record("latest-artifact", "reports", "Locate latest artifact by type", ["data/system", "outputs/system"], ["locator_only", "not_run_daily"]),
    _record("artifact-browser", "reports", "Generate human artifact browser", ["data/system", "outputs/system"], ["browser_only", "not_run_daily"]),
    _record("quick-status", "reports", "Generate quick project status", ["data/system", "outputs/system"], ["status_only", "not_run_daily"]),
    _record("usability-audit", "audits", "Audit usability polish release candidate", ["data/system", "outputs/audit"], ["audit_only", "not_run_daily"]),
    _record("forward-dry-run-readiness", "audits", "Audit readiness to prepare 30 trading-day forward dry-run", ["data/system", "outputs/system", "outputs/audit"], ["readiness_only", "not_run_daily", "does_not_start_forward_dry_run"]),
    _record("external-project-intake", "planning", "Scan external research repos and write v0.7 A-share selection planning artifacts", ["data/system", "outputs/system", "docs"], ["intake_only", "not_run_daily", "no_broker", "no_real_orders", "no_third_party_code_merge"]),
]


def build_cli_inventory(paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    inventory_id, created_at = timestamp_id("CLIINV")
    payload = {
        "inventory_id": inventory_id,
        "created_at": created_at,
        "commands": sorted(COMMANDS, key=lambda item: item["command"]),
        "boundary": {
            "inventory_only": True,
            "run_daily_called": False,
            "write_main_ledger": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
        "warnings": [],
    }
    json_path = paths.data_dir / "system" / "cli_inventory.json"
    report_path = paths.outputs_dir / "system" / "CLI_INVENTORY.md"
    write_json_markdown(json_path, payload, report_path, build_cli_inventory_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_cli_inventory_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# CLI Inventory",
        "",
        "| command | category | purpose | writes_to | safety |",
        "|---|---|---|---|---|",
    ]
    for command in payload["commands"]:
        lines.append(
            f"| {command['command']} | {command['category']} | {command['purpose']} | {', '.join(command['writes_to'])} | {', '.join(command['safety'])} |"
        )
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "- inventory only",
            "- run-daily not called",
            "- no orders/trades/portfolio/accounts written",
            "",
        ]
    )
    return "\n".join(lines)
