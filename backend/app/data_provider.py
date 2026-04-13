from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import requests

try:
    import MetaTrader5 as mt5
except Exception:  # pragma: no cover
    mt5 = None

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X"


class DataProvider:
    def __init__(self, symbol: str = "XAUUSD") -> None:
        self.symbol = symbol
        self.last_price = 2350.0
        self.mt5_ready = self._init_mt5()

    def _init_mt5(self) -> bool:
        if mt5 is None:
            return False
        try:
            if not mt5.initialize():
                return False
            return mt5.symbol_select(self.symbol, True)
        except Exception:
            return False

    def fetch_ohlc(self, interval: str = "5m", rng: str = "5d") -> pd.DataFrame:
        if not self.mt5_ready:
            raise RuntimeError("MT5 is required for realtime data but not available")
        df = self._fetch_mt5_ohlc(interval, rng)
        if df.empty:
            raise RuntimeError("Unable to fetch OHLC from MT5")
        self.last_price = float(df["close"].iloc[-1])
        return df

    def fetch_10y_training_data(self) -> pd.DataFrame:
        if self.mt5_ready:
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=3650)
            rates = mt5.copy_rates_range(self.symbol, mt5.TIMEFRAME_H1, start, end)
            if rates is not None and len(rates) > 0:
                frame = pd.DataFrame(rates)
                frame["timestamp"] = pd.to_datetime(frame["time"], unit="s", utc=True)
                return frame[["timestamp", "open", "high", "low", "close", "tick_volume"]].rename(columns={"tick_volume": "volume"})

        url = YAHOO_CHART_URL
        params = {"interval": "60m", "range": "10y"}
        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        data = response.json()["chart"]["result"][0]
        quote = data["indicators"]["quote"][0]
        return pd.DataFrame(
            {
                "timestamp": pd.to_datetime(data["timestamp"], unit="s", utc=True),
                "open": quote["open"],
                "high": quote["high"],
                "low": quote["low"],
                "close": quote["close"],
                "volume": quote.get("volume"),
            }
        ).dropna(subset=["close"])

    def fetch_live_price(self) -> dict:
        if not self.mt5_ready:
            raise RuntimeError("MT5 is required for realtime price but not available")
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick:
            raise RuntimeError("Unable to fetch live tick from MT5")

        spread = float(tick.ask - tick.bid)
        mid = float((tick.ask + tick.bid) / 2)
        self.last_price = mid
        return {
            "price": mid,
            "bid": float(tick.bid),
            "ask": float(tick.ask),
            "spread": spread,
            "timestamp": datetime.now(timezone.utc),
        }

    def _fetch_mt5_ohlc(self, interval: str, rng: str) -> pd.DataFrame:
        tf_map = {"1m": mt5.TIMEFRAME_M1, "5m": mt5.TIMEFRAME_M5, "15m": mt5.TIMEFRAME_M15, "1h": mt5.TIMEFRAME_H1}
        timeframe = tf_map.get(interval, mt5.TIMEFRAME_M5)
        bars = 500 if rng in {"1d", "5d"} else 1500
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, bars)
        if rates is None or len(rates) == 0:
            return pd.DataFrame()
        frame = pd.DataFrame(rates)
        frame["timestamp"] = pd.to_datetime(frame["time"], unit="s", utc=True)
        return frame[["timestamp", "open", "high", "low", "close", "tick_volume"]].rename(columns={"tick_volume": "volume"})

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
