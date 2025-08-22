import ccxt
from ..config import settings
class Markets:
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
        self.markets = self.ex.load_markets()
    def amount_to_precision(self, symbol: str, amount: float) -> float:
        try:
            return float(self.ex.amount_to_precision(symbol, amount))
        except Exception:
            return amount
    def price_to_precision(self, symbol: str, price: float) -> float:
        try:
            return float(self.ex.price_to_precision(symbol, price))
        except Exception:
            return price
