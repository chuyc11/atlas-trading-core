"""Local package locator facade for global-briefing historical packages."""

from __future__ import annotations

from typing import Any

from trading_core.global_briefing.real_package_manifest import build_global_briefing_package_manifest
from trading_core.storage.file_paths import ProjectPaths


def locate_real_global_briefing_packages(
    *,
    root: str | None = None,
    include: list[str] | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    return build_global_briefing_package_manifest(root=root, include=include, paths=paths)
