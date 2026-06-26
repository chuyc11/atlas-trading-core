"""Local import shim for running the src-layout package before installation."""

from pathlib import Path
import pkgutil

__version__ = "0.6.3.1"

__path__ = pkgutil.extend_path(__path__, __name__)

SRC_PACKAGE_DIR = Path(__file__).resolve().parents[1] / "src" / "trading_core"
if SRC_PACKAGE_DIR.is_dir():
    src_package_path = str(SRC_PACKAGE_DIR)
    if src_package_path not in __path__:
        __path__.append(src_package_path)
