"""Local import shim for running the src-layout package before installation."""

import re
from pathlib import Path
import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)

SRC_PACKAGE_DIR = Path(__file__).resolve().parents[1] / "src" / "trading_core"
if SRC_PACKAGE_DIR.is_dir():
    src_package_path = str(SRC_PACKAGE_DIR)
    if src_package_path not in __path__:
        __path__.append(src_package_path)


def _read_src_version() -> str:
    src_init = SRC_PACKAGE_DIR / "__init__.py"
    if src_init.exists():
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', src_init.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    version_path = Path(__file__).resolve().parents[1] / "VERSION"
    if version_path.exists():
        match = re.search(r"v(\d+\.\d+\.\d+)", version_path.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    return "0.0.0"


__version__ = _read_src_version()
