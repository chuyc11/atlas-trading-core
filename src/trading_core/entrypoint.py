"""Lightweight installed CLI entry point.

Version checks intentionally avoid importing the large command dispatcher so a
broken optional command module cannot make ``trading-core --version`` fail.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from trading_core import __version__


def run_load_macro(arguments: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="trading-core load-macro")
    parser.add_argument("--date", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(arguments)

    from trading_core.signals.macro_signal_loader import sync_macro_signals
    from trading_core.storage.file_paths import project_paths

    rows, limitations = sync_macro_signals(
        args.date,
        project_paths(),
        write_local=not args.dry_run,
    )
    print({"macro_signals": len(rows), "limitations": limitations})
    return 1 if limitations else 0


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["--version"]:
        print(f"trading-core {__version__}")
        return 0
    if arguments and arguments[0] == "load-macro":
        return run_load_macro(arguments[1:])

    from trading_core.cli import main as cli_main

    return cli_main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
