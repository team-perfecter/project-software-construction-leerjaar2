from fastapi import APIRouter, Depends, HTTPException
from api.auth_utils import get_current_user
from api.auth_utils_admin import require_admin
from api.models.reservation_model import ReservationModel
from api.datatypes.reservation import ReservationCreate
from api.datatypes.user import User

router = APIRouter(tags=["admin-reservations"])

reservation_model = ReservationModel()


@router.post("/admin/reservations")
async def admin_create_reservation(
        reservation: ReservationCreate,
        current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    new_id = reservation_model.create_reservation(reservation)
    return {"message": "Reservation created", "reservation_id": new_id}


@router.delete("/admin/reservations/{reservation_id}")
async def admin_delete_reservation(
        reservation_id: int,
        current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    deleted = reservation_model.delete_reservation(reservation_id)
    if not deleted:
        raise HTTPException(404, "Reservation not found")

    return {"message": "Reservation deleted"}