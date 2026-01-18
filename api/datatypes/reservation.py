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
  end_time: datetime | None
  user_id: int | None
  cost: int
  status: str
  discount_code: Optional[str] = None


class Reservation(ReservationCreate):
  id: int
  created_at: datetime
