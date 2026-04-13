from __future__ import annotations

import pandas as pd

from .indicators import compute_indicators, latest_indicator_snapshot
from .patterns import detect_candlestick_confirmation
from .strategy import derive_rule_signal


def run_backtest(raw_df: pd.DataFrame, quantity: float = 1.0, target_profit: float = 10.0, stop_loss: float = 5.0) -> dict:
    df = compute_indicators(raw_df)
    position = None
    entry = 0.0
    pnl_total = 0.0
    wins, losses = 0, 0

    for i in range(30, len(df)):
        window = df.iloc[: i + 1]
        snap = latest_indicator_snapshot(window)
        pattern = detect_candlestick_confirmation(window)
        signal, _ = derive_rule_signal(snap, pattern)
        price = snap["price"]

        if position is None and signal in {"BUY", "SELL"}:
            position = signal
            entry = price
            continue

        if position:
            pnl = (price - entry) * quantity if position == "BUY" else (entry - price) * quantity
            if pnl >= target_profit or pnl <= -stop_loss:
                pnl_total += pnl
                if pnl >= 0:
                    wins += 1
                else:
                    losses += 1
                position = None

    total = wins + losses
    win_rate = (wins / total) if total else 0
    return {"trades": total, "wins": wins, "losses": losses, "win_rate": win_rate, "pnl": pnl_total}
