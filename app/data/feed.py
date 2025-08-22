import ccxt, pandas as pd
from ..config import settings
class DataFeed:
    def __init__(self):
        args = {'enableRateLimit': True, 'options': {'defaultType': 'spot'}}
        if settings.BINANCE_API_KEY:
            args.update({'apiKey': settings.BINANCE_API_KEY, 'secret': settings.BINANCE_API_SECRET})
        self.ex = ccxt.binance(args)
        if settings.BINANCE_TESTNET:
            try:
                self.ex.set_sandbox_mode(True)
            except Exception:
                pass
    def ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 500):
        data = self.ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(data, columns=['ts','open','high','low','close','volume'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms', utc=True)
        df.set_index('ts', inplace=True)
        return df
    def last_price(self, symbol: str):
        return float(self.ex.fetch_ticker(symbol)['last'])
    def equity_usdt(self) -> float:
        try:
            balances = self.ex.fetch_balance()
            total_usdt = balances['total'].get('USDT', 0.0)
            for coin in ('BTC','ETH','SOL','XRP'):
                qty = balances['total'].get(coin, 0.0)
                if qty:
                    price = self.last_price(f"{coin}/USDT")
                    total_usdt += qty * price
            return float(total_usdt)
        except Exception:
            return 0.0
