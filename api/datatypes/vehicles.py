from dataclasses import dataclass

@dataclass
class Vehicles:
    user_id: int
    license_plate: str
    make: str
    model: str
    color: str
    year: int