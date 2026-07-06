"""Audit v3.8.0 data edge/microstructure artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_release_chain import audit_release_artifacts, spec_by_key
from trading_core.equity_release_chain.generic import DEFAULT_AS_OF_DATE
from trading_core.storage.file_paths import ProjectPaths


def audit_a_share_v38_data_edge_microstructure(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    return audit_release_artifacts(spec=spec_by_key("v38"), as_of_date=as_of_date, paths=paths)
