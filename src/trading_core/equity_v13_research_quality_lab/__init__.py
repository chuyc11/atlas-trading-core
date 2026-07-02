"""v1.3.0 A-share autonomous research quality and strategy lab expansion."""

from trading_core.equity_v13_research_quality_lab.audit import audit_a_share_v13_research_quality_lab
from trading_core.equity_v13_research_quality_lab.builder import DEFAULT_AS_OF_DATE, run_a_share_v13_research_quality_lab

__all__ = [
    "DEFAULT_AS_OF_DATE",
    "audit_a_share_v13_research_quality_lab",
    "run_a_share_v13_research_quality_lab",
]
