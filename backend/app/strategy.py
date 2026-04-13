from .config import settings


def derive_rule_signal(snapshot: dict, pattern: str) -> tuple[str, str]:
    rsi = snapshot["rsi_14"]
    bullish_cross = snapshot["bullish_cross"]
    bearish_cross = snapshot["bearish_cross"]

    buy_bias = rsi < 38 or bullish_cross
    sell_bias = rsi > 62 or bearish_cross

    if rsi < 35 and bullish_cross:
        return "BUY", "RSI oversold + MACD bullish crossover"
    if rsi > 65 and bearish_cross:
        return "SELL", "RSI overbought + MACD bearish crossover"

    if pattern == "BULLISH_ENGULFING" and buy_bias:
        return "BUY", "Aggressive buy from candlestick confirmation"
    if pattern == "BEARISH_ENGULFING" and sell_bias:
        return "SELL", "Aggressive sell from candlestick confirmation"

    if buy_bias and not sell_bias:
        return "BUY", "Loosened aggressive buy filter"
    if sell_bias and not buy_bias:
        return "SELL", "Loosened aggressive sell filter"

    return "HOLD", "No clean edge yet"


def combine_with_ml(rule_signal: str, buy_probability: float) -> tuple[str, float]:
    sell_probability = 1 - buy_probability
    if rule_signal == "BUY" and buy_probability >= settings.min_confidence:
        return "BUY", buy_probability
    if rule_signal == "SELL" and sell_probability >= settings.min_confidence:
        return "SELL", sell_probability

    if buy_probability >= 0.7:
        return "BUY", buy_probability
    if sell_probability >= 0.7:
        return "SELL", sell_probability

    return "HOLD", max(buy_probability, sell_probability)
