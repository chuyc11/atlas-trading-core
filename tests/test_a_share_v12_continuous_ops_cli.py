from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v12_test_utils import make_v12_paths


def test_v12_cli_run_audit_operator_commands_and_owner_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v12_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "owner_daily_status_output", lambda **_: '{"known_owner_readiness_state":"blocked"}')

    assert cli.main(["plan-a-share-local-post-close-schedule", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["run-a-share-v12-continuous-ops", "--as-of-date", "2026-07-01", "--simulation-only", "--dry-run"]) == 0
    assert cli.main(["run-a-share-v12-continuous-ops", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-local-scheduler-plan", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-operator-runbook", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-continuous-simulation-history", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-incident-remediation-pack", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-artifact-index-and-health-report", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["audit-a-share-v12-continuous-ops", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["run-and-audit-a-share-v12-continuous-ops", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["owner-daily-status", "--as-of-date", "2026-07-01", "--format", "json"]) == 0


def test_v12_cli_requires_simulation_only_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v12_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["run-a-share-v12-continuous-ops", "--as-of-date", "2026-07-01"]) == 1
