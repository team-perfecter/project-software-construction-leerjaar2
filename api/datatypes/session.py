from dataclasses import dataclass
from datetime import datetime
from parking_lot import Parking_lot
# from payment import Payment
from user import User
from vehicles import Vehicles


@dataclass
class Session:
    id: int
    parking_lot_id: Parking_lot.id
    payment_id: int  # Payment.id
    user_id: User.id
    vehicle_id: Vehicles.id
    start_time: datetime
    end_time: datetime
    duration_in_minutes: int
    cost: float
    payment_status: str


""" data
json
"1": {
        "id": "1",
        "parking_lot_id": "5",
        "payment_id": "10",
        "user_id": "3",
        "vehicle_id": "7",
        "start_time": "2023-06-15T08:30:00",
        "end_time": "2023-06-15T10:00:00",
        "duration_in_minutes": 90,
        "cost": 3.5
    }"1": {
        "id": "1",
        "parking_lot_id": "1",
        "licenseplate": "JO-227-4",
        "started": "2020-03-25T20:29:47Z",
        "stopped": "2020-03-26T05:10:47Z",
        "user": "natasjadewit",
        "duration_minutes": 521,
        "cost": 16.5,
        "payment_status": "paid"
    },
    "2": {
        "id": "2",
        "parking_lot_id": "1",
        "licenseplate": "SQ-90-LMD",
        "started": "2020-03-26T12:23:12Z",
        "stopped": "2020-03-26T21:19:12Z",
        "user": "cindy.adriaanse1",
        "duration_minutes": 536,
        "cost": 16.97,
        "payment_status": "paid"
    }
db
"id": "1",
"parking_lot_id": "5",
"payment_id": "10",
"user_id": "3",
"vehicle_id": "7",
"start_time": "2023-06-15 08:30:00",
"end_time": "2023-06-15 10:00:00",
"duration_in_minutes": 90,
"cost": 3.5
"""
