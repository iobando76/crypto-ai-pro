from dataclasses import dataclass
@dataclass
class RuntimeState:
    equity_usdt: float = 300.0
state = RuntimeState()
