"""Audit v3.9.0 owner handoff documentation artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_release_chain import audit_release_artifacts, spec_by_key
from trading_core.equity_release_chain.generic import DEFAULT_AS_OF_DATE
from trading_core.storage.file_paths import ProjectPaths


def audit_a_share_v39_owner_handoff_docs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    return audit_release_artifacts(spec=spec_by_key("v39"), as_of_date=as_of_date, paths=paths)
