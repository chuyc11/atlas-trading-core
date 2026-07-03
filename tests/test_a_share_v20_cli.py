from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v20_test_utils import make_v20_paths


def test_v20_cli_build_audit_specialty_commands_and_owner_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v20_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "owner_daily_status_output", lambda **_: '{"known_owner_readiness_state":"blocked"}')

    assert cli.main(["build-a-share-v20-platform-closeout", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-v20-plan-book-capability-map", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-v20-release-lineage", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-v20-safety-boundary-sweep", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-v20-platform-health-report", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-v20-owner-release-dashboard", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-v20-known-limitations-and-next-phase", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["audit-a-share-v20-platform-closeout", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-and-audit-a-share-v20-platform-closeout", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["owner-daily-status", "--as-of-date", "2026-07-01", "--format", "json"]) == 0


def test_v20_cli_requires_simulation_only_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v20_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v20-platform-closeout", "--as-of-date", "2026-07-01"]) == 1
    assert cli.main(["build-a-share-v20-plan-book-capability-map", "--as-of-date", "2026-07-01"]) == 1
