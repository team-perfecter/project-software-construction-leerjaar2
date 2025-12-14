from datetime import datetime
from pydantic import BaseModel

class Reservation(BaseModel):
  id: int
  user_id: int
  vehicle_id: int
  parking_lot_id: int
  start_time: datetime
  end_time: datetime
  status: str
  created_at: datetime
  cost: int

class ReservationCreate(BaseModel):
  vehicle_id: int
  parking_lot_id: int
  start_date: datetime
  end_date: datetime