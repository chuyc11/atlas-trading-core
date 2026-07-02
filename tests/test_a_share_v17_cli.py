from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v17_test_utils import make_v17_paths


def test_v17_cli_build_audit_specialty_commands_and_owner_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v17_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "owner_daily_status_output", lambda **_: '{"known_owner_readiness_state":"blocked"}')

    assert cli.main(["build-a-share-v17-strategy-validation-lab", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-factor-validation-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-candidate-ranking-validation", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-strategy-oos-walkforward-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-robustness-statistical-validation", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-strategy-admission-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-experiment-validation-registry", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["audit-a-share-v17-strategy-validation-lab", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-and-audit-a-share-v17-strategy-validation-lab", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["owner-daily-status", "--as-of-date", "2026-07-01", "--format", "json"]) == 0


def test_v17_cli_requires_simulation_only_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v17_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v17-strategy-validation-lab", "--as-of-date", "2026-07-01"]) == 1
    assert cli.main(["build-a-share-factor-validation-review", "--as-of-date", "2026-07-01"]) == 1
