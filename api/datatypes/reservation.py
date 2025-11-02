from dataclasses import dataclass
from datetime import date
@dataclass
class Reservation:
    id: int
    vehicle_id: int
    user_id: int
    parking_lot_id: int
    start_time: date
    end_time: date
    status: str
    created_at: date
    cost: int