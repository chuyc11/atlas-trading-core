"""Build v3.8.0 data contract edge-case and microstructure validation artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_release_chain import run_release_artifacts, spec_by_key
from trading_core.equity_release_chain.generic import DEFAULT_AS_OF_DATE
from trading_core.storage.file_paths import ProjectPaths


def run_a_share_v38_data_edge_microstructure(
    *, as_of_date: str = DEFAULT_AS_OF_DATE, simulation_only: bool = False, paths: ProjectPaths | None = None
) -> dict[str, Any]:
    return run_release_artifacts(spec_by_key("v38"), as_of_date=as_of_date, simulation_only=simulation_only, paths=paths)
