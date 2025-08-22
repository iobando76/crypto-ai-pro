from dataclasses import dataclass
@dataclass
class RiskConfig:
    equity_usdt: float
    risk_per_trade: float
    daily_max_drawdown: float
    max_concurrent_positions: int
def position_size(entry: float, sl: float, equity_usdt: float, risk_frac: float) -> float:
    sl_dist = abs(entry - sl)
    if sl_dist <= 0:
        return 0.0
    risk_usd = equity_usdt * risk_frac
    qty = risk_usd / sl_dist
    return max(qty, 0.0)
def dynamic_position_size(entry: float, sl: float, equity_usdt: float, base_risk_frac: float, atr: float = None, max_notional_frac: float = 0.2) -> float:
    sl_dist = abs(entry - sl)
    if sl_dist <= 0 or equity_usdt <= 0:
        return 0.0
    vol_scale = 1.0
    if atr and atr > 0:
        ratio = (entry / atr)
        vol_scale = max(0.5, min(2.0, ratio / 500.0))
    risk_usd = equity_usdt * base_risk_frac * vol_scale
    qty = risk_usd / sl_dist
    max_notional = equity_usdt * max_notional_frac
    notional = qty * entry
    if notional > max_notional:
        qty = max_notional / entry
    return max(qty, 0.0)
