from datetime import datetime, time
from zoneinfo import ZoneInfo
from ..config import settings
TZ = ZoneInfo(settings.TIMEZONE)
def in_trading_window(now: datetime | None = None) -> bool:
    now = now or datetime.now(TZ)
    start_h, start_m = map(int, settings.TRADING_START.split(':'))
    end_h, end_m = map(int, settings.TRADING_END.split(':'))
    start = time(hour=start_h, minute=start_m, tzinfo=TZ)
    end = time(hour=end_h, minute=end_m, tzinfo=TZ)
    return start <= now.timetz() <= end
def local_now() -> datetime:
    return datetime.now(TZ)
