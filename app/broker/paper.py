from dataclasses import dataclass
@dataclass
class PaperOrder:
    symbol: str
    side: str
    qty: float
    entry: float
    tp: float
    sl: float
class PaperBroker:
    def place_bracket_market(self, symbol: str, side: str, qty: float, entry: float, tp: float, sl: float):
        return {"paper": True, "symbol": symbol, "side": side, "qty": qty, "entry": entry, "tp": tp, "sl": sl}
