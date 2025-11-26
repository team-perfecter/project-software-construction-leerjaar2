from pydantic import BaseModel

class VehicleCreate(BaseModel):
    user_id: int
    license_plate: str
    make: str
    model: str
    color: str
    year: int


class Vehicle(BaseModel):
    id: int