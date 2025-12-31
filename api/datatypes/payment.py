from datetime import date
from pydantic import BaseModel
from typing import Optional


class PaymentCreate(BaseModel):
    user_id: int
    transaction: Optional[str] = None
    amount: float
    method: Optional[str] = None
    issuer: Optional[str] = None
    bank: Optional[str] = None


class Payment(PaymentCreate):
    id: int
    date: date
    hash: str
    completed: bool
    refund_requested: bool


class PaymentUpdate(BaseModel):
    user_id: int
    transaction: Optional[str] = None
    amount: float
    method: Optional[str] = None
    issuer: Optional[str] = None
    bank: Optional[str] = None
    completed: bool
    refund_requested: bool
