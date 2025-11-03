from datetime import datetime, date
from pydantic import BaseModel

class Payment(BaseModel):
  id: int
  user_id: int
  transaction: str
  amount: float
  created_at: datetime
  completed_at: datetime
  hash: str
  method: str
  issue: str
  bank: str
  date: date