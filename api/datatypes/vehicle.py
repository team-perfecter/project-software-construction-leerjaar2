from datetime import date
from pydantic import BaseModel


class Vehicle(BaseModel):
    id: int
    user_id: int
    license_plate: str
    make: str
    model: str
    color: str
    year: int
    created_at: date