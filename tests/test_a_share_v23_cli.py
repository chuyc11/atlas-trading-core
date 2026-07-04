from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v23_test_utils import make_v23_paths


def test_v23_cli_build_audit_specialty_commands_and_owner_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v23_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "owner_daily_status_output", lambda **_: '{"known_owner_readiness_state":"blocked"}')

    assert cli.main(["build-a-share-v23-operator-ux-journal", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-decision-journal", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-daily-research-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-periodic-research-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-report-artifact-index", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-warning-blocker-explanations", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-owner-operator-dashboard", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["audit-a-share-v23-operator-ux-journal", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-and-audit-a-share-v23-operator-ux-journal", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["owner-daily-status", "--as-of-date", "2026-07-01", "--format", "json"]) == 0


def test_v23_cli_requires_simulation_only_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v23_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v23-operator-ux-journal", "--as-of-date", "2026-07-01"]) == 1
    assert cli.main(["build-a-share-decision-journal", "--as-of-date", "2026-07-01"]) == 1
