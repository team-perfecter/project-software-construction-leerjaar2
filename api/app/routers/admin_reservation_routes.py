import logging
from fastapi import APIRouter, Depends, HTTPException
from api.auth_utils import require_role
from api.models.reservation_model import ReservationModel
from api.datatypes.reservation import ReservationCreate
from api.datatypes.user import User, UserRole
from api.models.user_model import UserModel

from api.models.vehicle_model import Vehicle_model
from api.models.parking_lot_model import ParkingLotModel


router = APIRouter(tags=["admin-reservations"])

reservation_model = ReservationModel()
user_model = UserModel()
vehicle_model = Vehicle_model()
parking_lot_model = ParkingLotModel()

@router.post("/admin/reservations")
async def admin_create_reservation(
        reservation: ReservationCreate,
        _ = require_role(UserRole.ADMIN, UserRole.SUPERADMIN)
):
    # Check of user bestaat.
    user = user_model.get_user_by_id(reservation.user_id)
    if not user:
        logging.info(
            "Failed to create reservation: User ID %i does not exist", 
            reservation.user_id
            )
        raise HTTPException(404, "User not found")

    # Check of vehicle bestaat.
    vehicle =  vehicle_model.get_one_vehicle(reservation.vehicle_id)
    if not vehicle:
        logging.info(
            "Failed to create reservation: Vehicle ID %i does not exist", 
            reservation.vehicle_id
            )
        raise HTTPException(404, "Vehicle not found")

    # Check of parking lot bestaat.
    parking_lot = parking_lot_model.get_parking_lot_by_lid(reservation.parking_lot_id)
    if not parking_lot:
        logging.info(
            "Failed to create reservation: Parking Lot ID %i does not exist", 
            reservation.parking_lot_id
            )
        raise HTTPException(404, "Parking lot not found")

    new_id = reservation_model.create_reservation(reservation)

    logging.info("Created reservation ID %i for user ID %i", new_id, reservation.user_id)

    return {"message": "Reservation created", "reservation_id": new_id}


@router.delete("/admin/reservations/{reservation_id}")
async def admin_delete_reservation(
        reservation_id: int,
        current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPERADMIN))
):
    # Check of de reservatie bestaat
    reservation = reservation_model.get_reservation_by_id(reservation_id)
    if not reservation:
        logging.info(
            "Admin ID %i tried deleting nonexistent Reservation ID %i",
            current_user.id, reservation_id
        )
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Verwijderen
    deleted = reservation_model.delete_reservation(reservation_id)
    if not deleted:
        logging.error(
            "Reservation ID %i existed but failed to delete (Admin ID %i)",
            reservation_id, current_user.id
        )
        raise HTTPException(status_code=500, detail="Failed to delete reservation")

    logging.info(
        "Admin ID %i successfully deleted Reservation ID %i",
        current_user.id, reservation_id
    )

    return {"message": "Reservation deleted"}
