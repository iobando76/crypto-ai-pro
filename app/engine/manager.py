from time import sleep
from sqlmodel import select
from ..config import settings
from ..db import get_session, EquitySnapshot, ExecLock
from ..utils.logger import logger
def _daily_dd_locked() -> bool:
    with get_session() as s:
        snaps = s.exec(select(EquitySnapshot).order_by(EquitySnapshot.at)).all()
        if not snaps:
            return False
        today = snaps[-1].at.date()
        today_snaps = [x for x in snaps if x.at.date() == today]
        if len(today_snaps) < 2:
            return False
        start_eq = today_snaps[0].equity_usdt
        current_eq = today_snaps[-1].equity_usdt
        dd = (start_eq - current_eq) / start_eq if start_eq > 0 else 0.0
        if dd >= settings.DAILY_MAX_DRAWDOWN:
            lock = s.exec(select(ExecLock).where(ExecLock.day == today)).first()
            if not lock:
                lock = ExecLock(day=today, locked=True)
                s.add(lock)
            else:
                lock.locked = True
            s.commit()
            logger.warning("lock_triggered", drawdown=dd)
            return True
    return False
def run_manager_loop():
    while True:
        try:
            if _daily_dd_locked():
                sleep(20)
                continue
        except Exception as e:
            logger.error("manager_error", error=str(e))
        sleep(20)
