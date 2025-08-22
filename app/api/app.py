from fastapi import FastAPI, HTTPException
from sqlmodel import select
from ..db import init_db, get_session, Signal as DBSig, Order
from ..config import settings
from ..engine.risk import position_size
from ..data.feed import DataFeed
from ..data.markets import Markets
from ..utils.telegram import send_telegram_message
from ..utils.timebox import in_trading_window
from ..utils.logger import logger
from ..engine.scheduler import start_scheduler
from ..state import state
app = FastAPI(title="Crypto Assistant API")
init_db()
start_scheduler()
feed = DataFeed()
mk = Markets()
try:
    if settings.BINANCE_TESTNET:
        from ..broker.paper import PaperBroker
        broker = PaperBroker()
    else:
        from ..broker.binance import BinanceExec
        broker = BinanceExec()
except Exception as e:
    logger.error("broker_init_error", error=str(e))
@app.get('/health')
def health():
    return {"ok": True}
@app.get('/account')
def account():
    eq = feed.equity_usdt()
    state.equity_usdt = eq
    return {"equity_usdt": eq, "pairs": settings.PAIRS}
@app.get('/signals')
def list_signals(status: str = 'pending'):
    with get_session() as s:
        rows = s.exec(select(DBSig).where(DBSig.status == status).order_by(DBSig.id.desc())).all()
        return [r.dict() for r in rows]
@app.post('/signals/{signal_id}/approve')
def approve_signal(signal_id: int, qty: float | None = None):
    if not in_trading_window():
        raise HTTPException(400, 'Fuera de la ventana operativa')
    with get_session() as s:
        sig = s.get(DBSig, signal_id)
        if not sig or sig.status != 'pending':
            raise HTTPException(404, 'Signal no encontrada o no pendiente')
        eq = feed.equity_usdt()
        state.equity_usdt = eq
        if qty is None:
            try:
                from ..engine.risk import dynamic_position_size
                df_tmp = feed.ohlcv(sig.symbol, timeframe='5m', limit=50)
                atr = float(df_tmp['atr'].iloc[-1]) if 'atr' in df_tmp.columns else None
                max_frac = settings.MAX_POSITION_NOTIONAL_VOLATILE if sig.timeframe == 'volatile' else settings.MAX_POSITION_NOTIONAL
                qty = dynamic_position_size(entry=sig.entry, sl=sig.sl, equity_usdt=eq, base_risk_frac=settings.RISK_PER_TRADE, atr=atr, max_notional_frac=max_frac)
            except Exception:
                qty = position_size(entry=sig.entry, sl=sig.sl, equity_usdt=eq, risk_frac=settings.RISK_PER_TRADE)
            try:
                qty = mk.amount_to_precision(sig.symbol, qty)
            except Exception:
                pass
        notional = qty * sig.entry
        cap_notional = eq * settings.MAX_POSITION_NOTIONAL
        if notional > cap_notional and sig.entry > 0:
            qty = mk.amount_to_precision(sig.symbol, cap_notional / sig.entry)
        order_res = broker.place_bracket_market(symbol=sig.symbol, side=sig.side, qty=qty, entry_price=sig.entry, tp=sig.tp, sl=sig.sl)
        sig.status = 'approved'
        order = Order(signal_id=sig.id, symbol=sig.symbol, side=sig.side, qty=qty, entry=sig.entry, sl=sig.sl, tp=sig.tp)
        s.add(order)
        s.add(sig)
        s.commit()
    msg = f"✅ <b>Orden aprobada</b>\n{sig.symbol} {sig.side.upper()} qty={qty}\nEntry={sig.entry:.4f} SL={sig.sl:.4f} TP={sig.tp:.4f}"
    try:
        import anyio
        anyio.run(send_telegram_message, msg)
    except Exception:
        pass
    return {"ok": True, "qty": qty}
@app.post('/signals/{signal_id}/reject')
def reject_signal(signal_id: int):
    with get_session() as s:
        sig = s.get(DBSig, signal_id)
        if not sig or sig.status != 'pending':
            raise HTTPException(404, 'Signal no encontrada o no pendiente')
        sig.status = 'rejected'
        s.add(sig)
        s.commit()
    return {"ok": True}
