"""
This file contains all dataclasses related to reservations.
"""

from datetime import datetime
from pydantic import BaseModel

class Reservation(BaseModel):
  id: int
  created_at: datetime

class ReservationCreate(BaseModel):
    user_id: int
    vehicle_id: int
    parking_lot_id: int
    status: str
    start_time: datetime
    end_time: datetime | None
    cost: int