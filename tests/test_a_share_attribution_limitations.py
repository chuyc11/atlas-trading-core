from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_attribution_limitations_required_language(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "attribution_limitations")
    text = "\n".join(payload["limitations"])
    assert "Realized multi-day attribution is not yet available." in text
    assert payload["realized_performance_attribution_available"] is False
