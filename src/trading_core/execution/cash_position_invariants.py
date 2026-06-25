"""Cash, position, and available-share invariant checks."""

from __future__ import annotations

from typing import Any


def check_cash_position_invariants(account: dict[str, Any]) -> dict[str, Any]:
    issues = []
    cash = float(account.get("cash", 0.0))
    if cash < -1e-9:
        issues.append("cash_negative")
    for position in account.get("positions", []):
        quantity = int(position.get("quantity", 0))
        available = int(position.get("available_quantity", 0))
        pending = int(position.get("pending_t1_quantity", 0))
        if quantity < 0:
            issues.append(f"{position.get('symbol')}:position_negative")
        if available < 0:
            issues.append(f"{position.get('symbol')}:available_negative")
        if available > quantity:
            issues.append(f"{position.get('symbol')}:available_exceeds_position")
        if pending < 0:
            issues.append(f"{position.get('symbol')}:pending_negative")
    return {"passed": not issues, "issues": issues}

