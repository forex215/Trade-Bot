from __future__ import annotations

from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

import requests

FOREX_FACTORY_XML = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"


class NewsFilter:
    def __init__(self) -> None:
        self.events: list[datetime] = []
        self.last_refresh: datetime | None = None

    def refresh(self) -> None:
        if self.last_refresh and datetime.now(timezone.utc) - self.last_refresh < timedelta(minutes=30):
            return
        try:
            resp = requests.get(FOREX_FACTORY_XML, timeout=8)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            parsed = []
            for item in root.findall("channel/item"):
                currency = (item.findtext("country") or "") + (item.findtext("currency") or "")
                impact = (item.findtext("impact") or "").lower()
                if "usd" not in currency.lower() and "xau" not in currency.lower():
                    continue
                if "high" not in impact:
                    continue
                date_str = item.findtext("date")
                time_str = item.findtext("time")
                dt = self._parse_ff_datetime(date_str, time_str)
                if dt:
                    parsed.append(dt)
            self.events = parsed
            self.last_refresh = datetime.now(timezone.utc)
        except Exception:
            return

    def is_news_time(self, now: datetime | None = None, lock_minutes: int = 45) -> bool:
        now = now or datetime.now(timezone.utc)
        self.refresh()
        for event_dt in self.events:
            if abs((event_dt - now).total_seconds()) <= lock_minutes * 60:
                return True
        return False

    @staticmethod
    def _parse_ff_datetime(date_str: str | None, time_str: str | None) -> datetime | None:
        if not date_str or not time_str:
            return None
        candidate = f"{date_str} {time_str}".strip().lower().replace(" ", "")
        for fmt in ["%m-%d-%Y%I:%M%p", "%m-%d-%Y%H:%M"]:
            try:
                return datetime.strptime(candidate, fmt).replace(tzinfo=timezone.utc)
            except Exception:
                continue
        return None
