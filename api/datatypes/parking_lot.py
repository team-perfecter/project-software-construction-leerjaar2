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
  status: Optional[str] = None
  closed_reason: Optional[str] = None
  closed_date: Optional[date] = None


class Parking_lot_create(BaseModel):
  name: str
  location: str
  address: str
  capacity: int
  tariff: float
  daytariff: float
  lat: float
  lng: float
  status: Optional[str] = None
  closed_reason: Optional[str] = None
  closed_date: Optional[date] = None
