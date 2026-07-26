"""Artifact inventory scanner."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative, timestamp_id, write_json_markdown


ARTIFACT_DIRS = [
    ("data/raw", "raw data", "import-prices/fetch-prices/merge-price-data", True, False),
    ("data/features", "feature artifacts", "build-features", True, False),
    ("data/labels", "label artifacts", "build-labels", True, False),
    ("data/ml", "ML artifacts", "build-ml-dataset/train-ml-shadow/predict-ml-shadow", True, False),
    ("data/shadow", "ML shadow artifacts", "generate-ml-shadow-signals/ml-shadow-leaderboard", True, False),
    ("data/experiments", "experiment artifacts", "experiment commands", True, False),
    ("data/reports", "research report summaries", "weekly-research-report/monthly-research-report", True, False),
    ("data/system", "system artifacts", "system commands", True, False),
    ("outputs/backtests", "backtest reports", "backtest/run-backtest-batch", False, True),
    ("outputs/replays", "replay reports", "replay commands", False, True),
    ("outputs/shadow", "shadow reports", "ML shadow commands", False, True),
    ("outputs/experiments", "experiment reports", "experiment commands", False, True),
    ("outputs/reports", "research reports", "report commands", False, True),
    ("outputs/system", "system reports", "system commands", False, True),
    ("outputs/audit", "audit reports", "audit commands", False, True),
]

KEY_ARTIFACTS = [
    ("data/experiments/mistake_pattern_library.json", "experiments", True, False),
    ("data/experiments/experiment_dashboard.json", "experiments", True, False),
    ("data/reports/weekly_research_summary-2026-06-17-2026-06-23.json", "reports", True, False),
    ("data/system/cli_inventory.json", "system", True, False),
    ("data/system/artifact_inventory.json", "system", True, False),
    ("data/system/system_smoke_test.json", "system", True, False),
    ("data/system/boundary_regression_audit.json", "system", True, False),
    ("data/system/system_integrity_audit.json", "system", True, False),
    ("outputs/audit/SYSTEM_INTEGRITY_AUDIT.md", "audit", False, True),
]


def build_artifact_inventory(paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    inventory_id, created_at = timestamp_id("ARTINV")
    artifacts: list[dict[str, Any]] = []
    for directory, artifact_type, cli, machine, human in ARTIFACT_DIRS:
        root = paths.project_root / directory
        files = sorted(path for path in root.rglob("*") if path.is_file()) if root.exists() else []
        artifacts.append(
            {
                "artifact": directory,
                "path": directory,
                "exists": root.exists(),
                "category": directory.split("/")[1] if "/" in directory else directory,
                "artifact_type": artifact_type,
                "generated_by": cli,
                "machine_readable": machine,
                "human_readable": human,
                "allowed_into_main_trading_chain": False,
                "file_count": len(files),
                "notes": [] if root.exists() else ["directory missing"],
            }
        )
    for path_text, category, machine, human in KEY_ARTIFACTS:
        path = paths.project_root / path_text
        artifacts.append(
            {
                "artifact": path.name,
                "path": relative(path, paths.project_root),
                "exists": path.exists(),
                "category": category,
                "machine_readable": machine,
                "human_readable": human,
                "allowed_into_main_trading_chain": False,
                "notes": [] if path.exists() else ["missing"],
            }
        )
    payload = {
        "inventory_id": inventory_id,
        "created_at": created_at,
        "artifacts": artifacts,
        "warnings": [f"missing artifact: {item['path']}" for item in artifacts if not item["exists"]],
        "boundary": {
            "inventory_only": True,
            "run_daily_called": False,
            "write_main_ledger": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "artifact_inventory.json"
    report_path = paths.outputs_dir / "system" / "ARTIFACT_INVENTORY.md"
    write_json_markdown(json_path, payload, report_path, build_artifact_inventory_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_artifact_inventory_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Artifact Inventory",
        "",
        "| artifact | path | exists | category | machine_readable | human_readable | main chain |",
        "|---|---|---|---|---|---|---|",
    ]
    for artifact in payload["artifacts"]:
        lines.append(
            f"| {artifact['artifact']} | {artifact['path']} | {str(artifact['exists']).lower()} | {artifact['category']} | {str(artifact['machine_readable']).lower()} | {str(artifact['human_readable']).lower()} | {str(artifact['allowed_into_main_trading_chain']).lower()} |"
        )
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "- inventory only",
            "- no orders/trades/portfolio/accounts written",
            "- artifacts are not live trading instructions",
            "",
        ]
    )
    return "\n".join(lines)
