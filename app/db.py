from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select
from .config import settings
engine = create_engine(settings.DB_URL, echo=False)
class Signal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    side: str
    entry: float
    sl: float
    tp: float
    timeframe: str
    rationale: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    type: str = "strategy"
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    signal_id: int
    exchange_order_id: Optional[str] = None
    symbol: str
    side: str
    qty: float
    entry: float
    sl: float
    tp: float
    status: str = "submitted"
    created_at: datetime = Field(default_factory=datetime.utcnow)
class Position(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    side: str
    qty: float
    avg_entry: float
    sl: float
    tp: float
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "open"
class EquitySnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    at: datetime = Field(default_factory=datetime.utcnow)
    equity_usdt: float
class ExecLock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    day: date
    locked: bool = False
def init_db():
    SQLModel.metadata.create_all(engine)
def get_session():
    return Session(engine)
