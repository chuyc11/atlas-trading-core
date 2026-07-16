"""Date-based path helpers for trading-core outputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def find_workspace_root(start: Path | None = None) -> Path:
    start = (start or Path(__file__)).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "work" / "trading-core").exists():
            return candidate
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").is_file() and (candidate / "src" / "trading_core").is_dir():
            return candidate
    raise FileNotFoundError(f"unable to discover trading-core workspace from {start}")


@dataclass(frozen=True)
class ProjectPaths:
    workspace_root: Path
    project_root_override: Path | None = None

    @property
    def project_root(self) -> Path:
        return (self.project_root_override or self.workspace_root / "work" / "trading-core").resolve()

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
    root = (workspace_root or find_workspace_root()).resolve()
    standalone = root if (root / "pyproject.toml").is_file() and (root / "src" / "trading_core").is_dir() else None
    return ProjectPaths(root, standalone)


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
    for directory in ["daily", "weekly", "monthly", "backtests", "evolution", "experiments"]:
        (paths.outputs_dir / directory).mkdir(parents=True, exist_ok=True)
