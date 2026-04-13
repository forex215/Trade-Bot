from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

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
        self.data_dir = Path("Data")
        self._replay_idx = 0
        self._cached_local = self._load_local_dataset()

    def _init_mt5(self) -> bool:
        if mt5 is None:
            return False
        try:
            if not mt5.initialize():
                return False
            return mt5.symbol_select(self.symbol, True)
        except Exception:
            return False

    def _load_local_dataset(self) -> pd.DataFrame:
        if not self.data_dir.exists():
            return pd.DataFrame()
        files = sorted(self.data_dir.glob("*.csv"))
        if not files:
            return pd.DataFrame()
        frames = []
        for file in files:
            try:
                df = pd.read_csv(file)
                normalized = self._normalize_ohlc(df)
                if not normalized.empty:
                    frames.append(normalized)
            except Exception:
                continue
        if not frames:
            return pd.DataFrame()
        out = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["timestamp"]).sort_values("timestamp")
        return out.reset_index(drop=True)

    def _normalize_ohlc(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = {c.lower(): c for c in df.columns}
        time_key = next((k for k in ["timestamp", "time", "datetime", "date"] if k in cols), None)
        open_key = next((k for k in ["open", "o"] if k in cols), None)
        high_key = next((k for k in ["high", "h"] if k in cols), None)
        low_key = next((k for k in ["low", "l"] if k in cols), None)
        close_key = next((k for k in ["close", "c"] if k in cols), None)
        vol_key = next((k for k in ["volume", "tick_volume", "vol", "v"] if k in cols), None)
        if not all([time_key, open_key, high_key, low_key, close_key]):
            return pd.DataFrame()
        out = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(df[cols[time_key]], utc=True, errors="coerce"),
                "open": pd.to_numeric(df[cols[open_key]], errors="coerce"),
                "high": pd.to_numeric(df[cols[high_key]], errors="coerce"),
                "low": pd.to_numeric(df[cols[low_key]], errors="coerce"),
                "close": pd.to_numeric(df[cols[close_key]], errors="coerce"),
                "volume": pd.to_numeric(df[cols[vol_key]], errors="coerce") if vol_key else 0,
            }
        ).dropna(subset=["timestamp", "open", "high", "low", "close"])
        return out

    def fetch_ohlc(self, interval: str = "5m", rng: str = "5d") -> pd.DataFrame:
        if self.mt5_ready:
            df = self._fetch_mt5_ohlc(interval, rng)
            if not df.empty:
                self.last_price = float(df["close"].iloc[-1])
                return df

        if not self._cached_local.empty:
            bars = 2000 if interval == "1m" else 1200 if interval == "5m" else 800
            sampled = self._cached_local.tail(bars).copy()
            self.last_price = float(sampled["close"].iloc[-1])
            return sampled.reset_index(drop=True)

        raise RuntimeError("No realtime source available: connect MT5 or add CSV files in Data/")

    def fetch_10y_training_data(self) -> pd.DataFrame:
        if not self._cached_local.empty:
            return self._cached_local.copy()

        if self.mt5_ready:
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=3650)
            rates = mt5.copy_rates_range(self.symbol, mt5.TIMEFRAME_H1, start, end)
            if rates is not None and len(rates) > 0:
                frame = pd.DataFrame(rates)
                frame["timestamp"] = pd.to_datetime(frame["time"], unit="s", utc=True)
                return frame[["timestamp", "open", "high", "low", "close", "tick_volume"]].rename(columns={"tick_volume": "volume"})

        response = requests.get(YAHOO_CHART_URL, params={"interval": "60m", "range": "10y"}, timeout=12)
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
        if self.mt5_ready:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick:
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

        if self._cached_local.empty:
            raise RuntimeError("No realtime source available: connect MT5 or add CSV files in Data/")

        row = self._cached_local.iloc[self._replay_idx % len(self._cached_local)]
        self._replay_idx += 1
        mid = float(row["close"])
        spread = max(0.08, abs(float(row["high"] - row["low"])) * 0.05)
        return {
            "price": mid,
            "bid": mid - spread / 2,
            "ask": mid + spread / 2,
            "spread": spread,
            "timestamp": datetime.now(timezone.utc),
        }

    def _fetch_mt5_ohlc(self, interval: str, rng: str) -> pd.DataFrame:
        tf_map = {"1m": mt5.TIMEFRAME_M1, "5m": mt5.TIMEFRAME_M5, "15m": mt5.TIMEFRAME_M15, "1h": mt5.TIMEFRAME_H1}
        timeframe = tf_map.get(interval, mt5.TIMEFRAME_M5)
        bars = 800 if rng in {"1d", "5d"} else 2000
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, bars)
        if rates is None or len(rates) == 0:
            return pd.DataFrame()
        frame = pd.DataFrame(rates)
        frame["timestamp"] = pd.to_datetime(frame["time"], unit="s", utc=True)
        return frame[["timestamp", "open", "high", "low", "close", "tick_volume"]].rename(columns={"tick_volume": "volume"})
