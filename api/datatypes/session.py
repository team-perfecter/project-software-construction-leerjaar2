from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SessionCreate(BaseModel):
    parking_lot_id: int
    user_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    license_plate: str = None
    reservation_id: Optional[int] = None


class Session(SessionCreate):
    id: int
    started: datetime
    stopped: Optional[datetime] = None
    cost: Optional[float] = None
