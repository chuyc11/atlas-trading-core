"""CLI command handlers extracted from the main() dispatch chain.

Handlers are grouped by domain (core, a_share, versions). Each handler
resolves shared dependencies through the cli module namespace at call
time (late binding), so tests monkeypatching cli attributes keep working
unchanged. To add a command: append a handler and registry entry in the
matching domain module and region (EARLY runs before the v31/release
chain in cli.main(), LATE runs after it).
"""

from trading_core.cli_dispatch.a_share import DISPATCH_HANDLERS_EARLY as _EARLY_A_SHARE, DISPATCH_HANDLERS_LATE as _LATE_A_SHARE
from trading_core.cli_dispatch.core import DISPATCH_HANDLERS_EARLY as _EARLY_CORE, DISPATCH_HANDLERS_LATE as _LATE_CORE
from trading_core.cli_dispatch.versions import DISPATCH_HANDLERS_EARLY as _EARLY_VERSIONS, DISPATCH_HANDLERS_LATE as _LATE_VERSIONS

DISPATCH_HANDLERS_EARLY: dict[str, object] = {**_EARLY_CORE, **_EARLY_A_SHARE, **_EARLY_VERSIONS}
DISPATCH_HANDLERS_LATE: dict[str, object] = {**_LATE_CORE, **_LATE_A_SHARE, **_LATE_VERSIONS}
