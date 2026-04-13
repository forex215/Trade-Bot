from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .backtesting import run_backtest
from .config import settings
from .data_provider import DataProvider
from .indicators import compute_indicators, latest_indicator_snapshot
from .logger import TradeLogger
from .ml_model import SignalModel
from .models import CloseTradeRequest, PriceResponse, SignalResponse, TradeHistoryResponse, TradeRequest
from .patterns import detect_candlestick_confirmation
from .sessions import is_active_trading_session
from .strategy import combine_with_ml, derive_rule_signal
from .telegram_alerts import TelegramAlerter
from .trading import PaperTrader

app = FastAPI(title="XAUUSD AI Scalper")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = DataProvider()
model = SignalModel()
trader = PaperTrader()
logger = TradeLogger(settings.db_path)
alerter = TelegramAlerter(settings.telegram_bot_token, settings.telegram_chat_id)


def _market_snapshot() -> tuple[dict, dict, str, str, float]:
    raw = provider.fetch_ohlc()
    enriched = compute_indicators(raw)
    model.train_if_needed(enriched)
    latest = latest_indicator_snapshot(enriched)
    pattern = detect_candlestick_confirmation(enriched)
    rule_signal, reason = derive_rule_signal(latest, pattern)
    buy_probability = model.predict_buy_probability(enriched.iloc[-1])
    signal, confidence = combine_with_ml(rule_signal, buy_probability)
    return latest, {"buy": buy_probability, "sell": 1 - buy_probability}, signal, reason, confidence


@app.get("/price", response_model=PriceResponse)
def price() -> PriceResponse:
    tick = provider.fetch_live_price()
    if trader.active_trade:
        updated = trader.update_trade(tick["price"])
        if updated:
            logger.upsert_trade(updated)
    return PriceResponse(symbol=settings.symbol, **tick)


@app.get("/signal", response_model=SignalResponse)
def signal() -> SignalResponse:
    latest, proba, ai_signal, reason, confidence = _market_snapshot()
    tick = provider.fetch_live_price()

    if not is_active_trading_session():
        ai_signal = "HOLD"
        reason = "Outside London/New York trading sessions"
    elif tick["spread"] > settings.spread_threshold:
        ai_signal = "HOLD"
        reason = f"Spread too high ({tick['spread']:.2f})"

    return SignalResponse(
        signal=ai_signal,
        confidence=confidence,
        win_probability=proba["buy"] if ai_signal != "SELL" else proba["sell"],
        lose_probability=proba["sell"] if ai_signal != "SELL" else proba["buy"],
        indicators=latest,
        reason=reason,
    )


@app.post("/trade")
def trade(req: TradeRequest):
    if trader.active_trade:
        raise HTTPException(status_code=400, detail="Trade already open")

    signal_resp = signal()
    if signal_resp.signal == "HOLD" and not req.side:
        raise HTTPException(status_code=400, detail="No strong signal. Force side via payload to override.")

    side = req.side or signal_resp.signal
    tick = provider.fetch_live_price()
    entry = tick["ask"] if side == "BUY" else tick["bid"]
    opened = trader.open_trade(side=side, price=entry, lot_size=req.lot_size, quantity=req.quantity, target_profit=req.target_profit_usd)
    logger.upsert_trade(opened)
    alerter.send(f"Opened {opened.side} #{opened.trade_id[:8]} @ {opened.entry_price:.2f}")
    return {"message": "Trade opened", "trade": opened}


@app.post("/close")
def close(req: CloseTradeRequest):
    if not trader.active_trade or trader.active_trade.trade_id != req.trade_id:
        raise HTTPException(status_code=404, detail="Active trade not found")
    tick = provider.fetch_live_price()
    closed = trader.close_trade(tick["price"])
    if not closed:
        raise HTTPException(status_code=500, detail="Close failed")
    logger.upsert_trade(closed)
    alerter.send(f"Closed {closed.side} #{closed.trade_id[:8]} PnL ${closed.pnl_usd:.2f}")
    return {"message": "Trade closed", "trade": closed}


@app.get("/history", response_model=TradeHistoryResponse)
def history() -> TradeHistoryResponse:
    return TradeHistoryResponse(trades=logger.list_trades())


@app.get("/backtest")
def backtest():
    raw = provider.fetch_ohlc(interval="15m", rng="1mo")
    return run_backtest(raw, quantity=settings.quantity, target_profit=settings.target_profit_usd)
