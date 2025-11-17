from typing import Optional

from pydantic import BaseModel
from datetime import date


class Parking_lot(BaseModel):
  id: int
  name: str
  location: str
  address: str
  capacity: int
  reserved: int
  tariff: float
  daytariff: float
  created_at: Optional[date] = None
  lat: float
  lng: float