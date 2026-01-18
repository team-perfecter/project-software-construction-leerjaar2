"""
This file contains all dataclasses related to sessions.
"""

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
    start_time: datetime
    end_time: Optional[datetime] = None
    cost: Optional[float] = None
