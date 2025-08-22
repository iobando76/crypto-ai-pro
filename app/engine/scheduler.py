from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import select
from ..config import settings
from ..data.feed import DataFeed
from ..engine.strategies import breakout_strategy, mean_reversion_strategy, quick_momentum_strategy
from ..engine.scanner import detect_volatile_opportunity
from ..db import get_session, Signal as DBSig, EquitySnapshot, ExecLock
from ..utils.logger import logger
from ..utils.timebox import in_trading_window, local_now
feed = DataFeed()
scheduler = BackgroundScheduler(timezone=settings.TIMEZONE)
def _snapshot_equity():
    try:
        eq = feed.equity_usdt()
    except Exception as e:
        logger.error("equity_read_error", error=str(e))
        return
    with get_session() as s:
        s.add(EquitySnapshot(equity_usdt=eq))
        s.commit()
def _reset_daily():
    with get_session() as s:
        today = local_now().date()
        q = select(ExecLock).where(ExecLock.day == today)
        lock = s.exec(q).first()
        if not lock:
            lock = ExecLock(day=today, locked=False)
            s.add(lock)
        s.commit()
def generate_signals():
    if not in_trading_window():
        logger.info("skip_signals_outside_window")
        return
    with get_session() as s:
        today = local_now().date()
        lock = s.exec(select(ExecLock).where(ExecLock.day == today)).first()
        if lock and lock.locked:
            logger.info("skip_signals_locked")
            return
    for symbol in settings.PAIRS:
        try:
            df = feed.ohlcv(symbol, timeframe='5m', limit=settings.LOOKBACK_BARS)
            last_n = min(len(df), 288)
            vol_sum = df['volume'].iloc[-last_n:].sum()
            last_price = float(df['close'].iloc[-1])
            notional_24h = vol_sum * last_price
            if notional_24h < settings.MIN_VOLUME_USD:
                logger.info("skip_pair_low_volume", symbol=symbol, notional_24h=notional_24h)
                continue
            sigs = []
            sigs += breakout_strategy(df, symbol, '5m')
            sigs += mean_reversion_strategy(df, symbol, '5m')
            try:
                sigs += quick_momentum_strategy(df, symbol, '5m')
            except Exception:
                pass
            with get_session() as s:
                for sig in sigs:
                    s.add(DBSig(symbol=sig.symbol, side=sig.side, entry=sig.entry, sl=sig.sl, tp=sig.tp, timeframe=sig.timeframe, rationale=sig.rationale, type='strategy'))
                s.commit()
        except Exception as e:
            logger.error("signal_error", symbol=symbol, error=str(e))
def start_scheduler():
    scheduler.add_job(_snapshot_equity, 'interval', minutes=15)
    scheduler.add_job(_reset_daily, 'cron', hour=0, minute=1)
    scheduler.add_job(generate_signals, 'interval', minutes=settings.SIGNAL_INTERVAL_MINUTES)
    scheduler.add_job(lambda: [detect_volatile_opportunity(sym) for sym in settings.PAIRS], 'interval', minutes=1)
    scheduler.start()
