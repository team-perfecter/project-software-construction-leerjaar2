"""
This file contains all dataclasses related to reservations.
"""

from datetime import datetime
from pydantic import BaseModel


class ReservationCreate(BaseModel):
  vehicle_id: int
  parking_lot_id: int
  start_time: datetime
  end_time: datetime | None
  user_id: int | None
  cost: int
  status: str


class Reservation(ReservationCreate):
  id: int
  created_at: datetime
