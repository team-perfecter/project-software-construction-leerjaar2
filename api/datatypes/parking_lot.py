"""
This file contains all dataclasses related to parking lots.
"""

from typing import Optional

from pydantic import BaseModel
from datetime import date


class ParkingLot(BaseModel):
    id: int
    name: str
    location: str
    address: str
    capacity: int
    reserved: int
    tariff: float
    daytariff: float
    created_at: Optional[date] = None
    lat: float
    lng: float
    status: Optional[str] = None
    closed_reason: Optional[str] = None
    closed_date: Optional[date] = None


class ParkingLotCreate(BaseModel):
    name: str
    location: str
    address: str
    capacity: int
    tariff: float
    daytariff: float
    lat: float
    lng: float
    status: Optional[str] = None
    closed_reason: Optional[str] = None
    closed_date: Optional[date] = None

class ParkingLotFilter(BaseModel):
    """
    Filter options for the find_parking_lots() method in the parking lot model.
    """
    lot_id: Optional[int] = None
    name: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    min_capacity: Optional[int] = None
    max_capacity: Optional[int] = None
    min_tariff: Optional[float] = None
    max_tariff: Optional[float] = None
    has_availability: Optional[bool] = None
