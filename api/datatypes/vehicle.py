from pydantic import BaseModel

class Vehicle(BaseModel):
    id: int
    owner_id: int
    license_plate: str
    brand: str
    model: str
    color: str
    year: int