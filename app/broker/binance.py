import ccxt
from ..config import settings
from ..data.markets import Markets
from ..utils.logger import logger
class BinanceExec:
    def __init__(self):
        params = {'enableRateLimit': True, 'options': {'defaultType': 'spot'}}
        if settings.BINANCE_API_KEY:
            params.update({'apiKey': settings.BINANCE_API_KEY, 'secret': settings.BINANCE_API_SECRET})
        self.ex = ccxt.binance(params)
        if settings.BINANCE_TESTNET:
            try:
                self.ex.set_sandbox_mode(True)
            except Exception:
                pass
        self.mk = Markets()
    def place_bracket_market(self, symbol: str, side: str, qty: float, entry_price: float, tp: float, sl: float) -> dict:
        qty = self.mk.amount_to_precision(symbol, qty)
        logger.info("place_bracket_market", symbol=symbol, side=side, qty=qty, entry=entry_price, tp=tp, sl=sl)
        order = self.ex.create_order(symbol=symbol, type='market', side=side, amount=qty)
        opp_side = 'sell' if side == 'buy' else 'buy'
        try:
            self.ex.create_order(symbol=symbol, type='limit', side=opp_side, amount=qty, price=self.mk.price_to_precision(symbol, tp), params={'timeInForce':'GTC'})
        except Exception:
            pass
        try:
            self.ex.create_order(symbol=symbol, type='stop_loss_limit', side=opp_side, amount=qty, price=self.mk.price_to_precision(symbol, sl), params={'stopPrice':self.mk.price_to_precision(symbol, sl),'timeInForce':'GTC'})
        except Exception:
            pass
        return order
