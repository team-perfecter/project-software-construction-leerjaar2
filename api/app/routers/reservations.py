# import logging
# from datetime import datetime
# from api.auth_utils import get_current_user
# from api.datatypes.user import User
# from fastapi import Depends, APIRouter, HTTPException, status, Body
# from api.datatypes.reservation import Reservation, ReservationCreate
# from api.datatypes.vehicle import Vehicle
# from api.models.parking_lot_model import ParkingLotModel
# from api.models.reservation_model import Reservation_model
# from api.models.vehicle_model import Vehicle_model

# router = APIRouter(
#     tags=["reservations"]
# )

# reservation_model: Reservation_model = Reservation_model()
# parkingLot_model: ParkingLotModel = ParkingLotModel()
# vehicle_model: Vehicle_model = Vehicle_model()

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S"
# )

# @router.get("/reservations/{vehicle_id}")
# async def reservations(vehicle_id: int, user: User = Depends(get_current_user)):
#     vehicle = vehicle_model.get_one_vehicle(vehicle_id)
#     if vehicle is None:
#         raise HTTPException(status_code=404, detail="Vehicle not found")

#     if vehicle.user_id != user.id:
#         raise HTTPException(status_code=403, detail="This vehicle does not belong to the logged in user")

#     reservation_list: list[Reservation] = reservation_model.get_reservation_by_vehicle(vehicle_id)

#     return reservation_list













# # @router.post("/create_reservation")
# # async def create_reservation(reservation: ReservationCreate = Body(...), user: User = Depends(get_current_user)):
# #     # In deze print zie je dat alles word meegestuurd dus ik snap het niet (Fuck my life)
# #     print(reservation, flush=True)

# #     # check for missing fields
# #     missing_fields: list[str] = []
# #     if not reservation.vehicle_id:
# #         missing_fields.append("vehicle")
# #     if not reservation.parking_lot_id:
# #         missing_fields.append("parking lot")
# #     if not reservation.start_date:
# #         missing_fields.append("start date")
# #     if not reservation.end_date:
# #         missing_fields.append("end date")
# #     if len(missing_fields) > 0:
# #         raise HTTPException(status_code = 400, detail = {"missing_fields": missing_fields})

# #     # check if the vehicle and parking lot exist

# #     parking_lot = parkingLot_model.get_parking_lot_by_id(reservation.parking_lot_id)
# #     if parking_lot == None:
# #         raise HTTPException(status_code = 404, detail = {"message": f"Parking lot does not exist"})

# #     # Dit is kapot vraag me niet waarom want probeer maar eens deze route te runnen: @router.get("/vehicles/{vehicle_id}")
# #     vehicle = vehicle_model.get_one_vehicle(reservation.vehicle_id)
# #     if vehicle == None:
# #         raise HTTPException(status_code = 404, detail = {"message": f"Vehicle does not exist"})


# #     # check if the vehicle belongs to the user
# #     if vehicle["user_id"] != user.id:
# #         raise HTTPException(status_code = 401, detail = {"message": f"Vehicle does not belong to this user"})

# #     # check if the parking lot has space left
# #     if parking_lot.reserved <= 0:
# #         raise HTTPException(status_code = 401, detail = {"message": f"No more space in this parking lot"})

# #     # check if the vehicle already has a reservation around that time
# #     conflicting_time: bool = False
# #     vehicle_reservations: list[Reservation] = reservation_model.get_reservation_by_vehicle(vehicle["id"])
# #     for reservation in vehicle_reservations:
# #         if reservation["start_date"] < reservation["end_date"] and reservation["end_date"] > reservation["start_date"]:
# #             conflicting_time = True
# #             break
# #     if conflicting_time:
# #         raise HTTPException(status_code = 401, detail = {"message": f"Requested date has an overlap with another reservation for this vehicle"})

# #     # check if start date is later than the current date
# #     if datetime.fromisoformat(reservation.start_date) <= datetime.now:
# #         raise HTTPException(status_code = 403, detail = {"message": f"invalid start date. The start date cannot be earlier than the current date. current date: {datetime.now}, received date: {datetime.fromisoformat(reservation.start_date)}"})

# #     # check if the end date is later than the start date
# #     if datetime.fromisoformat(reservation.start_date) >= datetime.fromisoformat(reservation.end_date):
# #         raise HTTPException(status_code = 403, detail = {"message": f"invalid start date. The start date cannot be later than the end date start date: {start_date}, end date: {end_date}"})

# #     # create a new reservation
# #     reservation_model.create_reservation(Reservation(None, vehicle_id, user.id, parking_lot_id, start_date, end_date, "status", datetime.now, parking_lot.tariff))
# #     return JSONResponse(content={"message": "Reservation created successfully"}, status_code=201)





# # @router.post("/create_reservation_rework")
# # async def create_reservation(reservation: ReservationCreate, user: User = Depends(get_current_user)):
# #     print("check 1")
# #     print(reservation.vehicle_id, flush=True)
# #     parking_lot = parkingLot_model.get_parking_lot_by_id(reservation.parking_lot_id)
# #     if parking_lot == None:
# #         raise HTTPException(status_code = 404, detail = {"message": f"Parking lot does not exist"})
    
    
# #     vehicle = vehicle_model.get_one_vehicle(reservation.vehicle_id)
# #     print("FINAL CHECK:")
# #     print(vehicle)
# #     if vehicle == None:
# #         raise HTTPException(status_code = 404, detail = {"message": f"Vehicle does not exist"})

# #     HTTPException(status_code = 201, detail = {"message": f"Vehicle and Parkinglot does exist {parking_lot}, {vehicle}"})
    










# # @router.delete("/reservations/{reservation_id}")
# # async def delete_reservation(reservation_id: int, current_user: User = Depends(get_current_user)):
# #     # Controleer of de reservatie bestaat
# #     reservation: Reservation | None = reservation_model.get_reservation_by_id(reservation_id)
# #     if reservation is None:
# #         logging.warning("User with id %i tried to delete a reservation that does not exist: %i", current_user.id, reservation_id)
# #         raise HTTPException(status_code=404, detail={"message": "Reservation not found"})

# #     # Controleer of de reservatie toebehoort aan de ingelogde gebruiker
# #     if reservation.user_id != current_user.id:
# #         logging.warning("User with id %i tried to delete a reservation that does not belong to them: %i", current_user.id, reservation_id)
# #         raise HTTPException(status_code=403, detail={"message": "This reservation does not belong to the logged-in user"})

# #     # Verwijder de reservatie
# #     success = reservation_model.delete_reservation(reservation_id)
# #     if not success:
# #         logging.error("Failed to delete reservation with id %i for user %i", reservation_id, current_user.id)
# #         raise HTTPException(status_code=500, detail={"message": "Failed to delete reservation"})

# #     logging.info("User with id %i successfully deleted reservation with id %i", current_user.id, reservation_id)
# #     return JSONResponse(content={"message": "Reservation deleted successfully"}, status_code=200)
