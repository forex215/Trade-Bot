import pandas as pd


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema_200"] = out["close"].ewm(span=200, adjust=False).mean()

    delta = out["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, 1e-9)
    out["rsi_14"] = 100 - (100 / (1 + rs))

    ema12 = out["close"].ewm(span=12, adjust=False).mean()
    ema26 = out["close"].ewm(span=26, adjust=False).mean()
    out["macd"] = ema12 - ema26
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]

    high_low = out["high"] - out["low"]
    high_close = (out["high"] - out["close"].shift()).abs()
    low_close = (out["low"] - out["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    out["atr_14"] = tr.rolling(14).mean()

    out["returns"] = out["close"].pct_change().fillna(0)
    out["volatility_20"] = out["returns"].rolling(20).std()
    return out.dropna().reset_index(drop=True)


def latest_indicator_snapshot(df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    prev = df.iloc[-2]
    bullish_cross = prev["macd"] <= prev["macd_signal"] and last["macd"] > last["macd_signal"]
    bearish_cross = prev["macd"] >= prev["macd_signal"] and last["macd"] < last["macd_signal"]
    return {
        "price": float(last["close"]),
        "rsi_14": float(last["rsi_14"]),
        "ema_200": float(last["ema_200"]),
        "macd": float(last["macd"]),
        "macd_signal": float(last["macd_signal"]),
        "returns": float(last["returns"]),
        "atr_14": float(last["atr_14"]),
        "volatility_20": float(last["volatility_20"]),
        "bullish_cross": bullish_cross,
        "bearish_cross": bearish_cross,
        "above_ema": float(last["close"]) >= float(last["ema_200"]),
    }
