from pydantic import BaseModel
class ApproveOrder(BaseModel):
    signal_id: int
    qty: float | None = None
