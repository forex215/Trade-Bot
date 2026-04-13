from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    symbol: str = "XAUUSD"
    lot_size: float = 0.1
    quantity: float = 1.0
    min_confidence: float = 0.65
    target_profit_usd: float = 10.0
    break_even_profit_usd: float = 5.0
    spread_threshold: float = 0.8
    rr_ratio: float = 2.0
    auto_trade_enabled: bool = False
    auto_trade_confidence: float = 0.75
    news_lock_minutes: int = 45
    poll_interval_seconds: int = 2
    db_path: str = "trade_logs.db"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
