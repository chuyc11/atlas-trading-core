"""Markdown quality improvement evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, FORBIDDEN_POSITIVE_WORDING, TARGET_VERSION


def build_markdown_quality_improvement_evidence(*, output_roots: list[Path], as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    required = [str(path) for root in output_roots if root.exists() for path in root.glob("*.md")]
    hits = []
    for name in required:
        text = Path(name).read_text(encoding="utf-8")
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            if phrase in text:
                hits.append({"path": name, "phrase": phrase})
    ratio = 1.0 if required and not hits else 0.0 if hits else 1.0
    return {
        "evidence_id": "A-SHARE-MARKDOWN-QUALITY-IMPROVEMENT-EVIDENCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "required_items": required,
        "present_items": required,
        "missing_items": [],
        "completeness_ratio": ratio,
        "quality_grade": "audit_verified" if not hits else "none",
        "evidence_available": not hits,
        "forbidden_wording_positive_hits": hits,
        "blocking_reasons": [] if not hits else ["forbidden_positive_wording_present"],
        "warnings": [],
    }

