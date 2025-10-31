from dataclasses import dataclass
from datetime import date

@dataclass
class Parking_lot:
  id: int
  name: str
  location: str
  address: str
  capacity: int
  reserved: int
  tariff: float
  daytariff: float
  created_at: date
  lat: float
  lng: float