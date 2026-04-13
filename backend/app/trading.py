from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .config import settings
from .models import TradeRecord


class PaperTrader:
    def __init__(self) -> None:
        self.active_trade: TradeRecord | None = None

    def open_trade(self, side: str, price: float, lot_size: float | None = None, quantity: float | None = None, target_profit: float | None = None) -> TradeRecord:
        lot = lot_size or settings.lot_size
        qty = quantity or settings.quantity
        tgt = target_profit or settings.target_profit_usd
        stop_gap = tgt / settings.rr_ratio

        stop_loss = price - stop_gap / qty if side == "BUY" else price + stop_gap / qty
        take_profit = price + tgt / qty if side == "BUY" else price - tgt / qty

        self.active_trade = TradeRecord(
            trade_id=str(uuid4()),
            side=side,
            status="OPEN",
            entry_price=price,
            current_price=price,
            quantity=qty,
            lot_size=lot,
            pnl_usd=0.0,
            stop_loss=stop_loss,
            take_profit=take_profit,
            opened_at=datetime.now(timezone.utc),
        )
        return self.active_trade

    def update_trade(self, price: float) -> TradeRecord | None:
        if not self.active_trade:
            return None

        trade = self.active_trade
        trade.current_price = price
        trade.pnl_usd = self._profit(trade.side, trade.entry_price, price, trade.quantity)

        if trade.pnl_usd >= settings.break_even_profit_usd:
            trade.stop_loss = trade.entry_price

        hit_target = trade.pnl_usd >= settings.target_profit_usd
        hit_sl = (trade.side == "BUY" and price <= trade.stop_loss) or (trade.side == "SELL" and price >= trade.stop_loss)
        if hit_target or hit_sl:
            trade.status = "CLOSED"
            trade.closed_at = datetime.now(timezone.utc)
            self.active_trade = None
        return trade

    def close_trade(self, price: float) -> TradeRecord | None:
        if not self.active_trade:
            return None
        trade = self.active_trade
        trade.current_price = price
        trade.pnl_usd = self._profit(trade.side, trade.entry_price, price, trade.quantity)
        trade.status = "CLOSED"
        trade.closed_at = datetime.now(timezone.utc)
        self.active_trade = None
        return trade

    @staticmethod
    def _profit(side: str, entry_price: float, current_price: float, quantity: float) -> float:
        if side == "BUY":
            return (current_price - entry_price) * quantity
        return (entry_price - current_price) * quantity
