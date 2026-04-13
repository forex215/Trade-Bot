import pandas as pd


def detect_candlestick_confirmation(df: pd.DataFrame) -> str:
    if len(df) < 3:
        return "NONE"

    c1, c2 = df.iloc[-2], df.iloc[-1]
    body1 = abs(c1["close"] - c1["open"])
    body2 = abs(c2["close"] - c2["open"])

    bullish_engulf = (
        c1["close"] < c1["open"]
        and c2["close"] > c2["open"]
        and c2["close"] >= c1["open"]
        and c2["open"] <= c1["close"]
        and body2 > body1
    )
    bearish_engulf = (
        c1["close"] > c1["open"]
        and c2["close"] < c2["open"]
        and c2["open"] >= c1["close"]
        and c2["close"] <= c1["open"]
        and body2 > body1
    )

    if bullish_engulf:
        return "BULLISH_ENGULFING"
    if bearish_engulf:
        return "BEARISH_ENGULFING"
    return "NONE"
