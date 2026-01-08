"""
This file contains all dataclasses related to sessions.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Session(BaseModel):
    id: int
    parking_lot_id: int
    payment_id: Optional[int] = None
    user_id: int
    vehicle_id: int
    started: datetime
    stopped: Optional[datetime] = None
    duration_in_minutes: Optional[int] = None
    cost: Optional[float] = None

class SessionCreate(BaseModel):
    parking_lot_id: int
    user_id: int
    vehicle_id: int

