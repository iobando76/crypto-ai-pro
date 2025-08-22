from typing import List
import pandas as pd
from .indicators import add_base_indicators
class Signal:
    def __init__(self, symbol: str, side: str, entry: float, sl: float, tp: float, timeframe: str, rationale: str, typ: str = "strategy"):
        self.symbol = symbol
        self.side = side
        self.entry = entry
        self.sl = sl
        self.tp = tp
        self.timeframe = timeframe
        self.rationale = rationale
        self.type = typ
def breakout_strategy(df: pd.DataFrame, symbol: str, timeframe: str = '5m') -> List[Signal]:
    df = add_base_indicators(df)
    if len(df) < 100:
        return []
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if not (last['ema20'] > last['ema50'] and last['adx'] > 20):
        return []
    N = 20
    trigger = df['high'].iloc[-N:].max()
    if last['close'] > trigger and prev['close'] <= trigger:
        atr = float(last['atr'])
        entry = float(last['close'])
        sl = entry - 1.5 * atr
        tp = entry + 2.0 * (entry - sl)
        return [Signal(symbol, 'buy', entry, sl, tp, timeframe, f"Breakout EMA20>EMA50 ADX>20 ATR={atr:.2f}")]
    return []
def mean_reversion_strategy(df: pd.DataFrame, symbol: str, timeframe: str = '5m') -> List[Signal]:
    df = add_base_indicators(df)
    if len(df) < 100:
        return []
    last = df.iloc[-1]
    in_range = (abs(last['ema20'] - last['ema50']) / last['close'] < 0.005) and (last['adx'] < 18)
    if not in_range:
        return []
    if last['close'] <= last['bb_low'] and last['rsi'] < 30:
        atr = float(last['atr'])
        entry = float(last['close'])
        sl = entry - 1.2 * atr
        tp = float(last['bb_mid'])
        if tp > entry:
            return [Signal(symbol, 'buy', entry, sl, tp, timeframe, f"MR banda baja + RSI ATR={atr:.2f}")]
    return []
def quick_momentum_strategy(df: pd.DataFrame, symbol: str, timeframe: str = '5m'):
    df = add_base_indicators(df)
    if len(df) < 50:
        return []
    last = df.iloc[-1]
    prev = df.iloc[-2]
    cond_trend = last['ema20'] > last['ema50']
    price_jump = (last['close'] - prev['close']) / prev['close'] > 0.03
    if cond_trend and price_jump and last['rsi'] < 85:
        atr = float(last['atr'])
        entry = float(last['close'])
        sl = entry - 1.0 * atr
        tp = entry + 1.5 * (entry - sl)
        return [Signal(symbol, 'buy', entry, sl, tp, timeframe, f"Quick momentum EMA trend + jump ATR={atr:.3f}")]
    return []
