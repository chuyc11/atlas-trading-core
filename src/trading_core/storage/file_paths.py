"""Date-based path helpers for trading-core outputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def find_workspace_root(start: Path | None = None) -> Path:
    start = (start or Path(__file__)).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "work" / "trading-core").exists():
            return candidate
    return Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class ProjectPaths:
    workspace_root: Path

    @property
    def project_root(self) -> Path:
        return self.workspace_root / "work" / "trading-core"

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def outputs_dir(self) -> Path:
        return self.project_root / "outputs"

    @property
    def global_briefing_data_dir(self) -> Path:
        return self.workspace_root / "work" / "global-briefing" / "data"

    def dated_jsonl(self, bucket: str, stem: str, date: str) -> Path:
        return self.data_dir / bucket / f"{stem}-{date}.jsonl"

    def dated_json(self, bucket: str, stem: str, date: str) -> Path:
        return self.data_dir / bucket / f"{stem}-{date}.json"

    def daily_report(self, date: str) -> Path:
        return self.outputs_dir / "daily" / f"virtual-trading-report-{date}.md"


def project_paths(workspace_root: Path | None = None) -> ProjectPaths:
    return ProjectPaths((workspace_root or find_workspace_root()).resolve())


def ensure_project_dirs(paths: ProjectPaths) -> None:
    directories = [
        "raw",
        "processed",
        "snapshots",
        "runtime",
        "macro_signals",
        "signals",
        "orders",
        "trades",
        "portfolios",
        "valuations",
        "benchmarks",
        "attribution",
        "backtests",
        "evolution",
        "experiments",
        "exports",
        "strategy_versions",
    ]
    for directory in directories:
        (paths.data_dir / directory).mkdir(parents=True, exist_ok=True)
    (paths.data_dir / "raw" / "prices").mkdir(parents=True, exist_ok=True)
    for directory in ["daily", "weekly", "monthly", "backtests", "evolution"]:
        (paths.outputs_dir / directory).mkdir(parents=True, exist_ok=True)
