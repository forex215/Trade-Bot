from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


SignalType = Literal["BUY", "SELL", "HOLD"]
TradeSide = Literal["BUY", "SELL"]
TradeStatus = Literal["OPEN", "CLOSED"]


class PriceResponse(BaseModel):
    symbol: str
    price: float
    bid: float
    ask: float
    spread: float
    timestamp: datetime


class SignalResponse(BaseModel):
    signal: SignalType
    confidence: float = Field(ge=0, le=1)
    win_probability: float = Field(ge=0, le=1)
    lose_probability: float = Field(ge=0, le=1)
    indicators: dict
    reason: str


class TradeRequest(BaseModel):
    side: Optional[TradeSide] = None
    lot_size: Optional[float] = None
    quantity: Optional[float] = None
    target_profit_usd: Optional[float] = None


class TradeRecord(BaseModel):
    trade_id: str
    side: TradeSide
    status: TradeStatus
    entry_price: float
    current_price: float
    quantity: float
    lot_size: float
    pnl_usd: float
    stop_loss: float
    take_profit: float
    opened_at: datetime
    closed_at: Optional[datetime] = None


class TradeHistoryResponse(BaseModel):
    trades: list[TradeRecord]


class CloseTradeRequest(BaseModel):
    trade_id: str


class AutoTradeRequest(BaseModel):
    enabled: bool


class AutoTradeStatus(BaseModel):
    enabled: bool
    min_confidence: float
