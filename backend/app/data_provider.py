from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X"


class DataProvider:
    def __init__(self) -> None:
        self.last_price = 2350.0

    def fetch_ohlc(self, interval: str = "5m", rng: str = "5d") -> pd.DataFrame:
        params = {"interval": interval, "range": rng}
        try:
            response = requests.get(YAHOO_CHART_URL, params=params, timeout=8)
            response.raise_for_status()
            data = response.json()["chart"]["result"][0]
            quote = data["indicators"]["quote"][0]
            frame = pd.DataFrame(
                {
                    "timestamp": pd.to_datetime(data["timestamp"], unit="s", utc=True),
                    "open": quote["open"],
                    "high": quote["high"],
                    "low": quote["low"],
                    "close": quote["close"],
                    "volume": quote.get("volume"),
                }
            ).dropna(subset=["close"])
            if not frame.empty:
                self.last_price = float(frame["close"].iloc[-1])
                return frame
        except Exception:
            pass
        return self._synthetic_ohlc()

    def fetch_live_price(self) -> dict:
        ohlc = self.fetch_ohlc(interval="1m", rng="1d")
        mid = float(ohlc["close"].iloc[-1]) if not ohlc.empty else self.last_price
        spread = max(0.15, min(0.8, abs(np.random.normal(0.35, 0.1))))
        return {
            "price": mid,
            "bid": mid - spread / 2,
            "ask": mid + spread / 2,
            "spread": spread,
            "timestamp": datetime.now(timezone.utc),
        }

    def _synthetic_ohlc(self, rows: int = 400) -> pd.DataFrame:
        ts = pd.date_range(end=datetime.now(timezone.utc), periods=rows, freq="5min")
        drift = np.random.normal(0, 0.25, rows).cumsum()
        base = self.last_price + drift
        close = np.round(base, 2)
        open_ = np.round(close + np.random.normal(0, 0.12, rows), 2)
        high = np.maximum(open_, close) + np.random.uniform(0.01, 0.35, rows)
        low = np.minimum(open_, close) - np.random.uniform(0.01, 0.35, rows)
        return pd.DataFrame(
            {
                "timestamp": ts,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": np.random.randint(100, 1000, rows),
            }
        )
