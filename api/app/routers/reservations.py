import logging
from datetime import datetime
from api.auth_utils import get_current_user
from api.datatypes.user import User
from fastapi import Depends, APIRouter, HTTPException, status, Body
from api.datatypes.reservation import Reservation, ReservationCreate
from api.datatypes.vehicle import Vehicle
from api.models.parking_lot_model import ParkingLotModel
from api.models.reservation_model import Reservation_model
from api.models.vehicle_model import Vehicle_model

router = APIRouter(tags=["reservations"])

reservation_model: Reservation_model = Reservation_model()
parkingLot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: Vehicle_model = Vehicle_model()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@router.get("/reservations/vehicle/{vehicle_id}")
async def reservations(vehicle_id: int, user: User = Depends(get_current_user)):
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if vehicle["user_id"] != user.id:
        raise HTTPException(
            status_code=403, detail="This vehicle does not belong to the logged in user"
        )

    reservation_list: list[Reservation] = reservation_model.get_reservation_by_vehicle(
        vehicle_id
    )

    return reservation_list


@router.post("/reservations/create", status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: ReservationCreate, user: User = Depends(get_current_user)
):
    parking_lot = parkingLot_model.get_parking_lot_by_lid(reservation.parking_lot_id)
    if parking_lot is None:
        raise HTTPException(
            status_code=404, detail={"message": "Parking lot does not exist"}
        )

    vehicle = vehicle_model.get_one_vehicle(reservation.vehicle_id)
    if vehicle is None:
        raise HTTPException(
            status_code=404, detail={"message": "Vehicle does not exist"}
        )

    conflicting_time: bool = False
    vehicle_reservations: list[Reservation] = (
        reservation_model.get_reservation_by_vehicle(vehicle["id"])
    )

    for res in vehicle_reservations:
        if (
            reservation.start_time < res["end_time"]
            and reservation.end_time > res["start_time"]
        ):
            conflicting_time = True
            break

    if conflicting_time:
        raise HTTPException(
            status_code=401,
            detail={
                "message": "Requested date has an overlap with another reservation for this vehicle"
            },
        )

    if reservation.start_time < datetime.now():
        raise HTTPException(
            status_code=403,
            detail={
                "message": f"Invalid start date. The start date cannot be earlier than the current date. Current: {datetime.now()}, Received: {reservation.start_time}"
            },
        )

    if reservation.start_time >= reservation.end_time:
        raise HTTPException(
            status_code=403,
            detail={
                "message": f"Invalid dates. Start date cannot be later than or equal to end date. Start: {reservation.start_time}, End: {reservation.end_time}"
            },
        )

    reservation_data = {
        "user_id": user.id,
        "parking_lot_id": reservation.parking_lot_id,
        "vehicle_id": reservation.vehicle_id,
        "start_time": reservation.start_time,
        "end_time": reservation.end_time,
        "status": "confirmed",
    }

    try:
        reservation_id = reservation_model.create_reservation(reservation_data)
        logging.info("User %i created reservation %i", user.id, reservation_id)

        return {
            "id": reservation_id,
            "user_id": user.id,
            "vehicle_id": reservation.vehicle_id,
            "parking_lot_id": reservation.parking_lot_id,
            "start_time": reservation.start_time.isoformat(),
            "end_time": reservation.end_time.isoformat(),
            "status": "confirmed",
            "cost": reservation.cost if reservation.cost else 0,
        }
    except Exception as e:
        logging.error("Failed to create reservation for user %i: %s", user.id, e)
        raise HTTPException(
            status_code=500, detail={"message": "Failed to create reservation"}
        )


@router.delete("/reservations/delete/{reservation_id}")
async def delete_reservation(
    reservation_id: int, user: User = Depends(get_current_user)
):
    # Controleer of de reservatie bestaat
    reservation: Reservation | None = reservation_model.get_reservation_by_id(
        reservation_id
    )
    if reservation is None:
        logging.warning(
            "User with id %i tried to delete a reservation that does not exist: %i",
            user.id,
            reservation_id,
        )
        raise HTTPException(
            status_code=404, detail={"message": "Reservation not found"}
        )

    # Controleer of de reservatie toebehoort aan de ingelogde gebruiker
    if reservation["user_id"] != user.id:
        logging.warning(
            "User with id %i tried to delete a reservation that does not belong to them: %i",
            user.id,
            reservation_id,
        )
        raise HTTPException(
            status_code=403,
            detail={
                "message": "This reservation does not belong to the logged-in user"
            },
        )

    # Verwijder de reservatie
    success = reservation_model.delete_reservation(reservation_id)
    if not success:
        logging.error(
            "Failed to delete reservation with id %i for user %i",
            reservation_id,
            user.id,
        )
        raise HTTPException(
            status_code=500, detail={"message": "Failed to delete reservation"}
        )

    logging.info(
        "User with id %i successfully deleted reservation with id %i",
        user.id,
        reservation_id,
    )
    raise HTTPException(
        detail={"message": "Reservation deleted successfully"}, status_code=200
    )
