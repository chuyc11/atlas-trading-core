"""Build v3.2.0 workflow performance, caching, and incremental build artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_release_chain import run_release_artifacts, spec_by_key
from trading_core.equity_release_chain.generic import DEFAULT_AS_OF_DATE
from trading_core.storage.file_paths import ProjectPaths


def run_a_share_v32_workflow_performance(
    *, as_of_date: str = DEFAULT_AS_OF_DATE, simulation_only: bool = False, paths: ProjectPaths | None = None
) -> dict[str, Any]:
    return run_release_artifacts(spec_by_key("v32"), as_of_date=as_of_date, simulation_only=simulation_only, paths=paths)
