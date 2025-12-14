from datetime import datetime
from pydantic import BaseModel

class Reservation(BaseModel):
  id: int
  created_at: datetime

class ReservationCreate(BaseModel):
    vehicle_id: int
    parking_lot_id: int
    start_time: datetime
    end_time: datetime
    user_id: int | None = None       # ✅ Maak optioneel
    status: str = "pending"          # ✅ Default value
    cost: int = 0                    # ✅ Default value