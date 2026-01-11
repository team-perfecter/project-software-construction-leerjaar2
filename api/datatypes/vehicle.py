from pydantic import BaseModel
from datetime import date

class VehicleCreate(BaseModel):
    user_id: int
    license_plate: str
    make: str
    model: str
    color: str
    year: int


class Vehicle(VehicleCreate):
    id: int
    created_at: date