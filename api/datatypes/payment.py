from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional

class PaymentCreate(BaseModel):
  user_id: int
  transaction: str
  amount: float
  completed: Optional[bool] = None
  hash: str
  method: str
  issuer: Optional[str] = None
  bank: Optional[str] = None
  date: date

class Payment(PaymentCreate):
  id: int
  created_at: datetime