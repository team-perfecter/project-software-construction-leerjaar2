from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ReservationCreate(BaseModel):
  vehicle_id: int
  parking_lot_id: int
  start_time: datetime
  end_time: datetime | None


class Reservation(ReservationCreate):
  user_id: int
  id: int
  created_at: datetime
  cost: int
  status: str
  discount_code: Optional[str] = None
