from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v24_test_utils import make_v24_paths


def test_v24_cli_build_audit_and_specialty_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v24_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v24-maintenance-quality", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-artifact-bloat-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-report-deduplication-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-cli-hygiene-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-shared-result-contract-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-test-maintenance-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-owner-maintenance-dashboard", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["audit-a-share-v24-maintenance-quality", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-and-audit-a-share-v24-maintenance-quality", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0


def test_v24_cli_requires_simulation_only_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v24_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v24-maintenance-quality", "--as-of-date", "2026-07-01"]) == 1
    assert cli.main(["build-a-share-artifact-bloat-review", "--as-of-date", "2026-07-01"]) == 1
