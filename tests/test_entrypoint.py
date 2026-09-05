from __future__ import annotations

from pathlib import Path

from trading_core import __version__
from trading_core.entrypoint import main
import pytest

pytestmark = pytest.mark.smoke


def test_version_path_does_not_import_large_cli(capsys) -> None:
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == f"trading-core {__version__}"


def test_load_macro_accepts_explicit_workspace_root(tmp_path: Path, capsys) -> None:
    source = tmp_path / "work" / "global-briefing" / "data" / "macro_signals-2026-08-01.jsonl"
    source.parent.mkdir(parents=True)
    source.write_text("", encoding="utf-8")

    assert main([
        "load-macro",
        "--workspace-root",
        str(tmp_path),
        "--date",
        "2026-08-01",
        "--dry-run",
        "--allow-empty",
    ]) == 0
    assert "'macro_signals': 0" in capsys.readouterr().out
