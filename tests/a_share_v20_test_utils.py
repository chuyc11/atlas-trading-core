from __future__ import annotations

import json
from pathlib import Path

from a_share_v19_test_utils import make_v19_paths
from trading_core.equity_v19_ml_validation_model_risk.audit import audit_a_share_v19_ml_validation_model_risk
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk
from trading_core.equity_v20_platform_closeout.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_v20_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_v19_paths(tmp_path)
    run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    audit_a_share_v19_ml_validation_model_risk(paths=paths)
    (paths.project_root / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    (paths.project_root / "RELEASE_NOTES.md").write_text(
        "# Release Notes\n\n"
        "## v1.9.0-a-share-ml-validation-model-risk-and-research-portfolio-integration-hardening\n\n"
        "- full pytest: `1944 passed, 1 skipped`\n",
        encoding="utf-8",
    )
    return paths


def v20_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE):
    path = paths.data_dir / "equity_v20_platform_closeout" / "daily" / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
