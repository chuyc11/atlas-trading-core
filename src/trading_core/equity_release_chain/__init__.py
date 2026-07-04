"""Shared v2.5-v3.0 A-share release chain builders and audits."""

from trading_core.equity_release_chain.generic import audit_release_artifacts, run_release_artifacts
from trading_core.equity_release_chain.specs import RELEASE_SPECS, command_to_spec, spec_by_key

__all__ = ["RELEASE_SPECS", "audit_release_artifacts", "command_to_spec", "run_release_artifacts", "spec_by_key"]
