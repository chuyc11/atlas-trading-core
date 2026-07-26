"""Build v0.7 external project intake report and A-share selection plan docs."""

from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from trading_core.external_intake.project_catalog import PROJECTS
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


TARGET_VERSION = "v0.7.0-external-project-intake-and-a-share-selection-plan"
RECOMMENDED_NEXT_VERSION = "v0.7.1-a-share-full-market-data-ingestion"
BOUNDARY = {
    "external_intake_only": True,
    "third_party_code_merged_into_main_flow": False,
    "day2_executed": False,
    "run_daily_called": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "llm_trading_decision": False,
    "model_profit_guaranteed": False,
    "etf_forward_dry_run_status_changed": False,
}


def build_external_project_intake(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    root = paths.project_root / "external_research"
    projects = [_project_record(paths, root, item) for item in PROJECTS]
    downloaded = [item for item in projects if item["downloaded"]]
    missing = [item["repo_name"] for item in projects if not item["downloaded"] and not item.get("optional")]
    payload: dict[str, Any] = {
        "intake_id": "EXTERNAL-PROJECT-INTAKE-V070",
        "target_version": TARGET_VERSION,
        "generated_from": "local external_research shallow clones and repository metadata scan",
        "external_research_root": "external_research",
        "projects_total": len(projects),
        "projects_downloaded": len(downloaded),
        "required_projects_missing": missing,
        "overall_passed": not missing,
        "blocking_reasons": [f"missing_required_external_repo: {name}" for name in missing],
        "projects": projects,
        "top_priority_repos": [item["repo_name"] for item in projects if item["integration_priority"] == "A"],
        "reuse_matrix": _reuse_matrix(projects),
        "v07_architecture": _architecture_payload(),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "boundary": dict(BOUNDARY),
    }
    docs = _write_docs(paths, payload)
    payload["generated_docs"] = docs
    json_path = paths.data_dir / "system" / "external_project_intake_report.json"
    report_path = paths.outputs_dir / "system" / "EXTERNAL_PROJECT_INTAKE_REPORT.md"
    write_json_markdown(json_path, payload, report_path, build_intake_markdown(payload))
    _write_roadmap_summary(paths, payload)
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _project_record(paths: ProjectPaths, root: Path, item: dict[str, Any]) -> dict[str, Any]:
    local_path = root / item["local_dir"]
    source_structure = _source_structure(local_path)
    license_detected = _license_detected(local_path)
    readme = _readme_summary(local_path)
    return {
        "repo_name": item["repo_name"],
        "github_url": item["github_url"],
        "local_path": _rel(local_path, paths.project_root),
        "downloaded": local_path.exists(),
        "optional": bool(item.get("optional", False)),
        "license_detected": license_detected,
        "main_language": _main_language(local_path),
        "project_focus": item["project_focus"],
        "usable_modules": _usable_modules(local_path, item["usable_modules"]),
        "reusable_design_patterns": item["reusable_design_patterns"],
        "integration_priority": item["integration_priority"],
        "integration_risk": item["integration_risk"],
        "requires_manual_review": item["requires_manual_review"],
        "can_import_directly": item["can_import_directly"],
        "recommended_action": item["recommended_action"],
        "source_structure": source_structure,
        "readme_summary": readme,
        "git_head": _git_value(local_path, ["rev-parse", "HEAD"]) if local_path.exists() else "",
        "git_remote": _git_value(local_path, ["remote", "get-url", "origin"]) if local_path.exists() else "",
    }


def _source_structure(local_path: Path) -> list[str]:
    if not local_path.exists():
        return []
    names = []
    for child in sorted(local_path.iterdir(), key=lambda item: item.name.lower()):
        if child.name == ".git":
            continue
        suffix = "/" if child.is_dir() else ""
        names.append(f"{child.name}{suffix}")
        if len(names) >= 30:
            break
    return names


def _license_detected(local_path: Path) -> str:
    if not local_path.exists():
        return "not_downloaded"
    for pattern in ["LICENSE*", "COPYING*", "NOTICE*"]:
        for path in local_path.glob(pattern):
            if path.is_file():
                first = path.read_text(encoding="utf-8", errors="ignore")[:500].lower()
                if "apache license" in first:
                    return "Apache"
                if "mit license" in first or "permission is hereby granted" in first:
                    return "MIT"
                if "gnu general public license" in first or "gpl" in first:
                    return "GPL"
                return path.name
    readme = _read_text(_find_readme(local_path))[:2000].lower()
    if "apache" in readme:
        return "Apache_in_readme"
    if "mit" in readme:
        return "MIT_in_readme"
    if "gpl" in readme:
        return "GPL_in_readme"
    return "not_detected"


def _main_language(local_path: Path) -> str:
    if not local_path.exists():
        return "not_downloaded"
    suffixes = Counter()
    code_suffixes = Counter()
    for path in local_path.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts or not path.is_file():
            continue
        if path.suffix:
            suffix = path.suffix.lower()
            if suffix in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".csv", ".json", ".yaml", ".yml", ".md", ".txt"}:
                suffixes[suffix] += 1
                continue
            if suffix in {".py", ".ipynb", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".h", ".m", ".r"}:
                code_suffixes[suffix] += 1
            suffixes[suffix] += 1
    selected = code_suffixes or suffixes
    if not selected:
        return "unknown"
    suffix, _count = selected.most_common(1)[0]
    return {
        ".py": "Python",
        ".ipynb": "Jupyter Notebook",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".md": "Markdown",
    }.get(suffix, suffix.lstrip(".").upper())


def _usable_modules(local_path: Path, configured: list[str]) -> list[dict[str, Any]]:
    modules = []
    for rel in configured:
        path = local_path / rel
        modules.append({"path": rel, "exists": path.exists(), "type": "dir" if path.is_dir() else "file" if path.is_file() else "missing"})
    return modules


def _find_readme(local_path: Path) -> Path | None:
    if not local_path.exists():
        return None
    for pattern in ["README.md", "README.rst", "README*"]:
        for path in local_path.glob(pattern):
            if path.is_file():
                return path
    return None


def _readme_summary(local_path: Path) -> dict[str, Any]:
    path = _find_readme(local_path)
    text = _read_text(path)
    headings = [line.strip("# ").strip() for line in text.splitlines() if line.startswith("#")][:8]
    return {
        "path": path.name if path else "",
        "exists": path is not None,
        "headings": headings,
        "chars_scanned": len(text),
    }


def _read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _git_value(path: Path, args: list[str]) -> str:
    try:
        return subprocess.run(["git", *args], cwd=path, check=False, capture_output=True, text=True, timeout=8).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _reuse_matrix(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "repo_name": project["repo_name"],
            "priority": project["integration_priority"],
            "immediate_use": project["project_focus"],
            "reuse_patterns": project["reusable_design_patterns"],
            "risk": project["integration_risk"],
            "direct_import_allowed": project["can_import_directly"],
            "manual_review_required": project["requires_manual_review"],
            "recommended_action": project["recommended_action"],
        }
        for project in projects
    ]


def _architecture_payload() -> dict[str, Any]:
    return {
        "positioning": "A-share full-market AI multi-horizon stock selection and virtual portfolio tracking system",
        "main_lines": [
            "A-share full-market stock selection is the main product line",
            "ETF forward dry-run remains benchmark/control group and execution-rule foundation",
            "Tonghuashun/miniQMT/broker adapters remain future research only",
        ],
        "v07_modules": [
            "external_intake",
            "integrations/public_data",
            "equity_universe",
            "equity_data",
            "equity_industry",
            "equity_fundamental",
            "equity_data_quality",
            "equity_features",
            "equity_scoring",
            "equity_selection",
            "equity_portfolios",
            "equity_briefing",
            "equity_validation",
            "integrations",
        ],
        "data_flow": [
            "public/local A-share provider adapters",
            "A-share universe and trading calendar",
            "daily price, adjusted price, daily basic, industry, and basic financial data panels",
            "coverage audit and schema audit",
            "tradability/liquidity/risk filters",
            "long/mid/short feature sets",
            "LongScore/MidScore/ShortScore/RiskScore/LiquidityScore/IndustryScore",
            "candidate pools and watchlists",
            "long/mid/short virtual portfolios",
            "daily Chinese owner briefing",
            "walk-forward validation",
        ],
        "boundaries": dict(BOUNDARY),
    }


def _write_docs(paths: ProjectPaths, payload: dict[str, Any]) -> list[str]:
    docs = {
        "A_SHARE_FULL_MARKET_AI_STOCK_SELECTION_PLAN.md": build_plan_doc(payload),
        "EXTERNAL_PROJECT_INTAKE.md": build_intake_doc(payload),
        "EXTERNAL_PROJECT_REUSE_MATRIX.md": build_reuse_matrix_doc(payload),
        "V0_7_ARCHITECTURE.md": build_architecture_doc(payload),
    }
    written = []
    for filename, content in docs.items():
        path = paths.project_root / "docs" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(_rel(path, paths.project_root))
    return written


def _write_roadmap_summary(paths: ProjectPaths, payload: dict[str, Any]) -> None:
    path = paths.outputs_dir / "system" / "V0_7_ROADMAP_SUMMARY.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_roadmap_summary(payload), encoding="utf-8")


def build_intake_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# External Project Intake Report",
        "",
        f"- target_version: {payload['target_version']}",
        f"- projects_total: {payload['projects_total']}",
        f"- projects_downloaded: {payload['projects_downloaded']}",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- recommended_next_version: {payload['recommended_next_version']}",
        "",
        "## Projects",
        "| repo | priority | downloaded | license | language | direct import | action |",
        "|---|---|---:|---|---|---:|---|",
    ]
    for project in payload["projects"]:
        lines.append(
            f"| {project['repo_name']} | {project['integration_priority']} | {str(project['downloaded']).lower()} | {project['license_detected']} | {project['main_language']} | {str(project['can_import_directly']).lower()} | {project['recommended_action']} |"
        )
    lines.extend(["", "## Boundary", *_boundary_lines(), ""])
    return "\n".join(lines)


def build_plan_doc(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A Share Full Market AI Stock Selection Plan",
            "",
            "## Positioning",
            "",
            "The project upgrades from an ETF virtual trading MVP into an A-share full-market AI multi-horizon stock selection and virtual portfolio tracking system.",
            "",
            "Priorities: stock selection quality, usability, daily executability, explainability, virtual portfolio tracking, and future adapter extensibility.",
            "",
            "## Product Lines",
            "",
            "- A-share full-market selection is the main line.",
            "- ETF forward dry-run remains execution-rule foundation, virtual ledger foundation, benchmark, and control group.",
            "- Tonghuashun, miniQMT, and broker adapters are future research only.",
            "",
            "## v0.7 Roadmap",
            "",
            "- v0.7.0 external project intake and A-share selection plan",
            "- v0.7.1 A-share full-market data ingestion",
            "  - outputs: `data/equity_universe/equity_master.parquet`, `data/equity_universe/trading_calendar.parquet`, `data/equity_market/daily_price_panel.parquet`, `data/equity_market/adjusted_price_panel.parquet`, `data/equity_market/daily_basic_panel.parquet`, `data/equity_industry/industry_classification.parquet`, `data/equity_fundamental/basic_financials_panel.parquet`, `data/equity_data_quality/a_share_data_source_manifest.json`, `data/equity_data_quality/a_share_data_coverage_audit.json`, `data/equity_data_quality/a_share_data_schema_audit.json`",
            "  - source priority: qstock-style public adapters, AkShare, Tushare if token exists, BaoStock, local CSV/Parquet, future Tonghuashun iFinD/QuantAPI",
            "  - constraints: data foundation only; no scores, candidates, virtual portfolios, broker, real orders, run-daily, or official forward dry-run day2",
            "- v0.7.2 tradable universe filter",
            "  - filters: ST/*ST, delisting board, suspended stocks, listing age below 120 trading days, less than 18 effective trading days in the last 20, 20-day average amount below 50 million CNY, market cap below 3 billion CNY, price below 2 CNY, severe missing fundamentals, one-word limit-up/down execution risk, unresolved abnormal volatility",
            "  - outputs: `tradable_universe.json`, `excluded_universe.json`, and `TRADABLE_UNIVERSE_REPORT.md`",
            "- v0.7.3 multi-horizon feature engineering",
            "  - long features: quality, ROE, gross margin, net margin, cash flow, leverage, valuation percentile, dividend, long-term trend",
            "  - mid features: 60/120-day trend, relative strength, industry rotation, earnings improvement, volume confirmation, volatility-adjusted return",
            "  - short features: 5/10/20-day momentum, breakout, pullback repair, volume-price confirmation, capital flow, short-term heat",
            "  - risk/liquidity/industry features are separate first-class feature groups",
            "- v0.7.4 Long/Mid/Short scoring system",
            "  - scores: LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, IndustryScore, CompositeOpportunityScore",
            "  - candidate gates: long 75/45/60, mid 75/55/65, short 80/65/75 for score/risk/liquidity",
            "- v0.7.5 candidate generation",
            "  - daily outputs: long 30, mid 30, short 30, watchlist 100-150, top 10 per horizon in the briefing",
            "- v0.7.6 three virtual portfolios",
            "  - portfolios: long 20-40, mid 20-40, short 10-30; virtual only",
            "- v0.7.7 daily AI stock selection briefing",
            "  - output: `outputs/equity_selection/daily/YYYY-MM-DD/DAILY_STOCK_SELECTION_BRIEFING.md`",
            "  - must state: research and virtual tracking only, not investment advice, no broker connection, no real orders, no profit guarantee",
            "- v0.7.8 historical walk-forward validation",
            "  - validates Top 10/Top 30 long/mid/short, composite pool, removal pool, and risk-alert pool on 5/10/20/60/120-day horizons",
            "- v0.7.9 30-day virtual forward tracking",
            "  - output: daily briefings plus `OWNER_30DAY_STOCK_SELECTION_BRIEFING.md`",
            "- v0.8.0 Tonghuashun, miniQMT, and simulated adapter research",
            "  - adapter research only: read-only quote/account sync, simulated adapter experiments, order preview, manual confirmation gate",
            "- v0.9.0 manual-confirmation trading preparation",
            "  - required gates: manual confirmation, kill switch, max position, max daily turnover, max drawdown stop, order preview diff, pre-trade risk check, post-trade reconciliation",
            "",
            "## Proposed Directories",
            "",
            "- `external_research/`",
            "- `src/trading_core/external_intake/`",
            "- `src/trading_core/integrations/public_data/`",
            "- `src/trading_core/equity_universe/`",
            "- `src/trading_core/equity_data/`",
            "- `src/trading_core/equity_industry/`",
            "- `src/trading_core/equity_fundamental/`",
            "- `src/trading_core/equity_data_quality/`",
            "- `src/trading_core/equity_features/`",
            "- `src/trading_core/equity_scoring/`",
            "- `src/trading_core/equity_selection/`",
            "- `src/trading_core/equity_portfolios/`",
            "- `src/trading_core/equity_briefing/`",
            "- `src/trading_core/equity_validation/`",
            "- `src/trading_core/integrations/`",
            "- `data/equity_universe/`, `data/equity_market/`, `data/equity_industry/`, `data/equity_fundamental/`, `data/equity_data_quality/`, `data/equity_features/`, `data/equity_scores/`, `data/equity_selection/`, `data/equity_portfolios/`, `data/equity_validation/`",
            "- `outputs/equity_selection/`, `outputs/equity_portfolios/`, `outputs/equity_validation/`",
            "",
            "## Required Boundary",
            "",
            *_boundary_lines(),
            "",
        ]
    )


def build_intake_doc(payload: dict[str, Any]) -> str:
    lines = [
        "# External Project Intake",
        "",
        "This document summarizes downloaded external repositories for design reference only.",
        "",
        "| repo | use | priority | risk | usable modules |",
        "|---|---|---|---|---|",
    ]
    for project in payload["projects"]:
        modules = ", ".join(item["path"] for item in project["usable_modules"] if item["exists"]) or "not found"
        lines.append(f"| {project['repo_name']} | {project['project_focus']} | {project['integration_priority']} | {project['integration_risk']} | {modules} |")
    lines.extend(["", "## Boundary", *_boundary_lines(), ""])
    return "\n".join(lines)


def build_reuse_matrix_doc(payload: dict[str, Any]) -> str:
    lines = [
        "# External Project Reuse Matrix",
        "",
        "| repo | priority | patterns to reuse | action | direct import allowed |",
        "|---|---|---|---|---:|",
    ]
    for row in payload["reuse_matrix"]:
        lines.append(
            f"| {row['repo_name']} | {row['priority']} | {', '.join(row['reuse_patterns'])} | {row['recommended_action']} | {str(row['direct_import_allowed']).lower()} |"
        )
    lines.extend(["", "## Integration Rule", "", "Do not merge third-party trading code into the main flow. All reuse must pass separate license, dependency, data reproducibility, and boundary review.", ""])
    return "\n".join(lines)


def build_architecture_doc(payload: dict[str, Any]) -> str:
    arch = payload["v07_architecture"]
    lines = [
        "# v0.7 Architecture",
        "",
        f"Positioning: {arch['positioning']}",
        "",
        "## Data Flow",
    ]
    lines.extend(f"- {item}" for item in arch["data_flow"])
    lines.extend(["", "## Modules"])
    lines.extend(f"- `src/trading_core/{item}/`" for item in arch["v07_modules"])
    lines.extend(
        [
            "",
            "## Mermaid",
            "",
            "```mermaid",
            "flowchart TD",
            '  P["Public / local A-share provider adapters"] --> U["Equity master and trading calendar"]',
            '  U --> M["Daily price / adjusted price / daily basic panels"]',
            '  U --> I["Industry and basic financial panels"]',
            '  M --> Q["Coverage audit and schema audit"]',
            '  I --> Q',
            '  Q --> B["Tradability / risk / liquidity filters"]',
            '  B --> C["Long / Mid / Short features"]',
            '  C --> D["LongScore / MidScore / ShortScore"]',
            '  D --> E["Candidates / watchlist / risk alerts"]',
            '  E --> F["Long / Mid / Short virtual portfolios"]',
            '  F --> G["Daily Chinese owner briefing"]',
            '  G --> H["Walk-forward validation"]',
            '  X["ETF forward dry-run"] --> J["Benchmark / control group"]',
            '  K["Future adapters"] -. "research only" .-> F',
            "```",
            "",
            "## v0.7.1 Data Foundation",
            "",
            "v0.7.1 writes audited local A-share data artifacts before any future filters, features, scores, candidates, or portfolios. Public provider gaps must be recorded in the source manifest and coverage audit.",
            "",
            "## Boundary",
            *_boundary_lines(),
            "",
        ]
    )
    return "\n".join(lines)


def build_roadmap_summary(payload: dict[str, Any]) -> str:
    lines = [
        "# v0.7 Roadmap Summary",
        "",
        f"- current release candidate: {payload['target_version']}",
        f"- external repos downloaded: {payload['projects_downloaded']}",
        f"- top priority repos: {', '.join(payload['top_priority_repos'])}",
        f"- recommended next version: {payload['recommended_next_version']}",
        "",
        "## Next",
        "",
        "v0.7.1 should build A-share full-market data ingestion with coverage audit before any scoring or candidate generation.",
        "",
        "## Boundary",
        *_boundary_lines(),
        "",
    ]
    return "\n".join(lines)


def _boundary_lines() -> list[str]:
    return [
        "- No real trading.",
        "- No broker connection.",
        "- No real orders.",
        "- No third-party trading code merged into the main flow.",
        "- No LLM direct trading decision.",
        "- No model profit guarantee.",
        "- ETF forward dry-run status unchanged.",
        "- `run-daily` not called.",
    ]
