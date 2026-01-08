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
