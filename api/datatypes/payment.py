"""
This file contains all dataclasses related to payments.
"""

from datetime import date
from pydantic import BaseModel
from typing import Optional


class PaymentCreate(BaseModel):
    user_id: Optional[int] = None
    parking_lot_id: int
    transaction: Optional[str] = None
    amount: float
    method: Optional[str] = None
    issuer: Optional[str] = None
    bank: Optional[str] = None
    reservation_id: Optional[int] = None
    session_id: Optional[int] = None


class Payment(PaymentCreate):
    id: int
    date: date
    hash: str
    completed: bool
    refund_requested: bool
    refund_accepted: bool
    admin_id: int


class PaymentUpdate(BaseModel):
    user_id: Optional[int] = None
    parking_lot_id: Optional[int] = None
    hash: Optional[str] = None
    transaction: Optional[str] = None
    amount: Optional[float] = None
    method: Optional[str] = None
    issuer: Optional[str] = None
    bank: Optional[str] = None
    completed: Optional[bool] = None
    refund_requested: Optional[bool] = None
