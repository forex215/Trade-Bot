from __future__ import annotations

import sqlite3
from datetime import datetime

from .models import TradeRecord


class TradeLogger:
    def __init__(self, path: str) -> None:
        self.path = path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id TEXT PRIMARY KEY,
                    side TEXT,
                    status TEXT,
                    entry_price REAL,
                    current_price REAL,
                    quantity REAL,
                    lot_size REAL,
                    pnl_usd REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    opened_at TEXT,
                    closed_at TEXT
                )
                """
            )

    def upsert_trade(self, trade: TradeRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO trades (
                    trade_id, side, status, entry_price, current_price, quantity, lot_size,
                    pnl_usd, stop_loss, take_profit, opened_at, closed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(trade_id) DO UPDATE SET
                    status=excluded.status,
                    current_price=excluded.current_price,
                    pnl_usd=excluded.pnl_usd,
                    stop_loss=excluded.stop_loss,
                    take_profit=excluded.take_profit,
                    closed_at=excluded.closed_at
                """,
                (
                    trade.trade_id,
                    trade.side,
                    trade.status,
                    trade.entry_price,
                    trade.current_price,
                    trade.quantity,
                    trade.lot_size,
                    trade.pnl_usd,
                    trade.stop_loss,
                    trade.take_profit,
                    trade.opened_at.isoformat(),
                    trade.closed_at.isoformat() if trade.closed_at else None,
                ),
            )

    def list_trades(self) -> list[TradeRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT trade_id, side, status, entry_price, current_price, quantity, lot_size, pnl_usd, stop_loss, take_profit, opened_at, closed_at FROM trades ORDER BY opened_at DESC"
            ).fetchall()

        trades = []
        for row in rows:
            trades.append(
                TradeRecord(
                    trade_id=row[0],
                    side=row[1],
                    status=row[2],
                    entry_price=row[3],
                    current_price=row[4],
                    quantity=row[5],
                    lot_size=row[6],
                    pnl_usd=row[7],
                    stop_loss=row[8],
                    take_profit=row[9],
                    opened_at=datetime.fromisoformat(row[10]),
                    closed_at=datetime.fromisoformat(row[11]) if row[11] else None,
                )
            )
        return trades
