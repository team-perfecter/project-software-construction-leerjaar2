import logging
from datetime import datetime

from api.auth_utils import get_current_user
from api.datatypes.payment import PaymentCreate
from api.datatypes.user import User
from api.models.parking_lot_model import ParkingLotModel
from api.models.payment_model import PaymentModel
from api.models.session_model import SessionModel
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import JSONResponse

from api.models.vehicle_model import Vehicle_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

router = APIRouter(tags=["sessions"])

session_model: SessionModel = SessionModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: Vehicle_model = Vehicle_model()
payment_model: PaymentModel = PaymentModel()


@router.post("/parking-lots/{lid}/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_parking_session(
    lid: int, vehicle_id: int, current_user: User = Depends(get_current_user)
):
    logging.info(
        "User with id %i attempting to start session at parking lot %i",
        current_user.id,
        lid,
    )

    # parking lot check
    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)
    if not parking_lot:
        logging.warning("Parking lot with id %i does not exist", lid)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot with ID {lid} does not exist",
            },
        )

    # vehicle en user check
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    logging.debug("Retrieved vehicle: %s", vehicle)

    if not vehicle:
        logging.warning("Vehicle with id %i does not exist", vehicle_id)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Vehicle not found",
                "message": f"Vehicle with ID {vehicle_id} does not exist",
            },
        )

    if vehicle["user_id"] != current_user.id:
        logging.warning(
            "User %i tried to start session with vehicle %i that doesn't belong to them",
            current_user.id,
            vehicle_id,
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Forbidden",
                "message": "Vehicle does not belong to current user",
            },
        )

    # active session check voor vehicle
    try:
        existing_sessions = session_model.get_all_sessions_by_id(lid, vehicle_id)
    except Exception as e:
        logging.error("Database error checking existing sessions: %s", e)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to check existing sessions",
            },
        )

    if existing_sessions:
        logging.warning(
            "Active session already exists for vehicle %i at parking lot %i",
            vehicle_id,
            lid,
        )
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Session already exists",
                "message": f"An active session already exists for this vehicle at this parking lot",
            },
        )

    # create new session
    try:
        session = session_model.create_session(lid, current_user.id, vehicle_id)
        if session is None:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Session creation failed",
                    "message": "This vehicle already has an active session",
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error("Failed to create session: %s", e)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to create session",
            },
        )

    logging.info(
        "Successfully started session for user %i at parking lot %i with vehicle %i",
        current_user.id,
        lid,
        vehicle_id,
    )

    return {
        "message": "Session started successfully",
        "session_id": session.get("id") if isinstance(session, dict) else None,
        "parking_lot_id": lid,
        "vehicle_id": vehicle_id,
        "license_plate": vehicle["license_plate"],
    }


@router.post("/parking-lots/{lid}/sessions/stop")
async def stop_parking_session(
    lid: int, vehicle_id: int, current_user: User = Depends(get_current_user)
):
    logging.info(
        "User %i attempting to stop session for vehicle %i", current_user.id, vehicle_id
    )

    try:
        active_sessions = session_model.get_vehicle_sessions(vehicle_id)
    except Exception as e:
        logging.error("Database error retrieving vehicle sessions: %s", e)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to retrieve active sessions",
            },
        )

    if not active_sessions:
        logging.info("No active sessions found for vehicle %i", vehicle_id)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No active session",
                "message": "This vehicle has no active sessions",
            },
        )

    try:
        session = session_model.stop_session(active_sessions)
        logging.debug("Stopped session: %s", session)
    except Exception as e:
        logging.error("Failed to stop session: %s", e)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to stop session",
            },
        )

    # Create payment
    try:
        payment: PaymentCreate = PaymentCreate(
            user_id=current_user.id, amount=session["cost"]
        )
        created_payment = payment_model.create_payment(payment)
        logging.info("Payment created for session with cost: %f", session["cost"])
    except Exception as e:
        logging.error("Failed to create payment: %s", e)
        # Session is already stopped, so we don't want to rollback
        # But we should notify the user
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Payment creation failed",
                "message": "Session stopped but payment could not be created. Please contact support.",
            },
        )

    return {
        "message": "Session stopped successfully",
        "session_id": session.get("id"),
        "cost": session["cost"],
        "duration_minutes": session.get("duration_in_minutes"),
        "payment_id": created_payment.get("id") if created_payment else None,
    }


@router.get("/sessions/active")
async def get_active_sessions(current_user: User = Depends(get_current_user)):
    """
    Geeft een lijst van alle actieve sessies.
    """
    logging.info("User %i requesting active sessions", current_user.id)

    try:
        sessions = session_model.get_active_sessions()
    except Exception as e:
        logging.error("Failed to retrieve active sessions: %s", e)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to retrieve active sessions",
            },
        )

    return {"active_sessions": sessions, "count": len(sessions) if sessions else 0}


@router.get("/sessions/vehicle/{vehicle_id}")
async def get_sessions_vehicle(vehicle_id: int, user: User = Depends(get_current_user)):
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if not vehicle or vehicle["user_id"] != user.id:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Vehicle not found",
                "message": f"Vehicle with ID {vehicle_id} does not exist",
            },
        )
    sessions = session_model.get_vehicle_sessions(vehicle_id)
    print(sessions)
    return JSONResponse(content={"message": sessions}, status_code=201)


# @router.get("/sessions/{session_id}")
# async def get_session_details(
#     session_id: int, current_user: User = Depends(get_current_user)
# ):
#     """
#     Haalt de details van een specifieke sessie op.
#     """
#     logging.info(
#         "User %i requesting details for session %i", current_user.id, session_id
#     )

#     try:
#         session = session_model.get_session_by_id(session_id)
#     except Exception as e:
#         logging.error("Failed to retrieve session %i: %s", session_id, e)
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "error": "Internal server error",
#                 "message": "Failed to retrieve session details",
#             },
#         )

#     if not session:
#         logging.warning("Session %i not found", session_id)
#         raise HTTPException(
#             status_code=404,
#             detail={
#                 "error": "Session not found",
#                 "message": f"Session with ID {session_id} does not exist",
#             },
#         )

#     return {"session": session}


# @router.update("/sessions/{session_id}")
# async def update_session_details(
#     session_id: int, end_time: datetime, current_user: User = Depends(get_current_user)
# ):
#     """
#     Update de details van een specifieke sessie.
#     """
#     logging.info(
#         "User %i attempting to update details for session %i",
#         current_user.id,
#         session_id,
#     )

#     try:
#         session = session_model.get_session_by_id(session_id)
#     except Exception as e:
#         logging.error("Failed to retrieve session %i for update: %s", session_id, e)
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "error": "Internal server error",
#                 "message": "Failed to retrieve session for update",
#             },
#         )

#     if not session:
#         logging.warning("Session %i not found for update", session_id)
#         raise HTTPException(
#             status_code=404,
#             detail={
#                 "error": "Session not found",
#                 "message": f"Session with ID {session_id} does not exist",
#             },
#         )

#     try:
#         updated_session = session_model.update_session_end_time(session_id, end_time)
#         logging.info("Session %i updated successfully", session_id)
#     except Exception as e:
#         logging.error("Failed to update session %i: %s", session_id, e)
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "error": "Internal server error",
#                 "message": "Failed to update session",
#             },
#         )

#     return {"message": "Session updated successfully", "session": updated_session}


# @router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_session(
#     session_id: int, current_user: User = Depends(get_current_user)
# ):
#     """
#     Verwijdert een specifieke sessie.
#     """
#     logging.info("User %i attempting to delete session %i", current_user.id, session_id)

#     try:
#         session = session_model.get_session_by_id(session_id)
#     except Exception as e:
#         logging.error("Failed to retrieve session %i for deletion: %s", session_id, e)
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "error": "Internal server error",
#                 "message": "Failed to retrieve session for deletion",
#             },
#         )

#     if not session:
#         logging.warning("Session %i not found for deletion", session_id)
#         raise HTTPException(
#             status_code=404,
#             detail={
#                 "error": "Session not found",
#                 "message": f"Session with ID {session_id} does not exist",
#             },
#         )

#     try:
#         session_model.delete_session(session_id)
#         logging.info("Session %i deleted successfully", session_id)
#     except Exception as e:
#         logging.error("Failed to delete session %i: %s", session_id, e)
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "error": "Internal server error",
#                 "message": "Failed to delete session",
#             },
#         )
