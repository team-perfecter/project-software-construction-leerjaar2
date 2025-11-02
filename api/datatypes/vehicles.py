from dataclasses import dataclass

@dataclass
class Vehicle:
    id: int
    user_id: int
    license_plate: str
    make: str
    model: str
    color: str
    year: int