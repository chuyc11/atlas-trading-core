"""A-share board-lot and odd-lot quantity rules."""

from __future__ import annotations

from typing import Any


BOARD_LOT = 100


def validate_order_quantity(side: str, quantity: int, *, position_quantity: int = 0, available_quantity: int = 0, board_lot: int = BOARD_LOT) -> dict[str, Any]:
    side = side.upper()
    if quantity <= 0:
        return {"accepted": False, "reason": "quantity_must_be_positive", "quantity": quantity}
    if side == "BUY":
        if quantity % board_lot != 0:
            return {"accepted": False, "reason": "buy_quantity_not_board_lot", "quantity": quantity}
        return {"accepted": True, "reason": "buy_board_lot_valid", "quantity": quantity}
    if side == "SELL":
        if quantity > position_quantity:
            return {"accepted": False, "reason": "sell_exceeds_position", "quantity": quantity}
        if quantity > available_quantity:
            return {"accepted": False, "reason": "sell_exceeds_available_shares", "quantity": quantity}
        return {"accepted": True, "reason": "sell_quantity_valid_odd_lot_allowed", "quantity": quantity}
    return {"accepted": False, "reason": "unsupported_side", "quantity": quantity}

