from api.auth_utils import get_current_user
from api.datatypes.parking_lot import Parking_lot
from api.datatypes.user import User
from api.storage.parking_lot_storage import Parking_lot_storage
from fastapi import HTTPException, APIRouter
import logging

router = APIRouter(
    tags=["Parking lots"]
)

storage: Parking_lot_storage = Parking_lot_storage()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@router.get("/parking_lot/{parking_lot_id}")
async def get_parking_lot_by_id(parking_lot_id: int, current_user: User = Depends(get_current_user)):
    # if not authenticated, raise httpexception
    logging.info("A user with the id of %i retrieved information about a parking lot with the id %i", 0, parking_lot_id)
    parking_lot: Parking_lot | None = storage.get_parking_lot_by_id(parking_lot_id)
    if parking_lot == None:
        logging.warning("Parking lot with the id %i does not exist", parking_lot_id)
        raise HTTPException(status_code = 404, details = {"message: ": f"Parking lot with id ${parking_lot_id} does not exist",})
    return parking_lot