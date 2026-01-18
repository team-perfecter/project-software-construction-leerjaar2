"""
This file contains all dataclasses related to reservations.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ReservationCreate(BaseModel):
  vehicle_id: int
  parking_lot_id: int
  start_time: datetime
  end_time: datetime
  user_id: Optional[int] = None
  cost: Optional[int] = None
  status: Optional[str] = None
  discount_code: Optional[str] = None


class Reservation(ReservationCreate):
  id: int
  created_at: datetime
