from __future__ import annotations

from trading_core import __version__
from trading_core.entrypoint import main


def test_version_path_does_not_import_large_cli(capsys) -> None:
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == f"trading-core {__version__}"
