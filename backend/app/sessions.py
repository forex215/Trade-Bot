from datetime import datetime, timezone


def is_active_trading_session(now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    h = now.hour
    london = 7 <= h <= 16
    new_york = 12 <= h <= 21
    return london or new_york
