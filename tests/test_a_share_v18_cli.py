from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v18_test_utils import make_v18_paths


def test_v18_cli_build_audit_specialty_commands_and_owner_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v18_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "owner_daily_status_output", lambda **_: '{"known_owner_readiness_state":"blocked"}')

    assert cli.main(["build-a-share-v18-research-db-feature-ml-lab", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-research-database-index", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-feature-store", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-label-store", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-pit-ml-dataset", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-offline-ml-model-lab", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-model-registry-and-cards", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-prediction-registry", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["audit-a-share-v18-research-db-feature-ml-lab", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-and-audit-a-share-v18-research-db-feature-ml-lab", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["owner-daily-status", "--as-of-date", "2026-07-01", "--format", "json"]) == 0


def test_v18_cli_requires_simulation_only_flag_for_model_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v18_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v18-research-db-feature-ml-lab", "--as-of-date", "2026-07-01"]) == 1
    assert cli.main(["build-a-share-offline-ml-model-lab", "--as-of-date", "2026-07-01"]) == 1
