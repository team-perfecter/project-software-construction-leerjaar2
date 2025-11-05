from datetime import datetime
from typing import List, Optional
from api.datatypes.session import Session


class Session_storage:
    """In-memory opslag voor parkeersessies (testversie, zonder database)."""

    def __init__(self):
        #Tijdelijke opslag van sessies
        self.session_list: list[Session] = []

    #Nieuwe sessie starten
    def start_session(self, vehicle_id: int, user_id: int, parking_lot_id: int = 1) -> None:
        #Controleer of dit voertuig al een actieve sessie heeft
        for s in self.session_list:
            if s["vehicle_id"] == vehicle_id and s["stopped"] is None:
                raise Exception("Vehicle already has an active session.")

        new_session = {
            "id": len(self.session_list) + 1,
            "vehicle_id": vehicle_id,
            "user_id": user_id,
            "parking_lot_id": parking_lot_id,
            "started": datetime.now(),
            "stopped": None,
            "duration_minutes": None,
            "cost": None,
        }
        self.session_list.append(new_session)
        return new_session

    #Actieve sessie stoppen
    def stop_session(self, vehicle_id: int) -> None:
        for s in self.session_list:
            if s["vehicle_id"] == vehicle_id and s["stopped"] is None:
                s["stopped"] = datetime.now()
                duration = (s["stopped"] - s["started"]).total_seconds() / 60
                s["duration_minutes"] = int(duration)
                s["cost"] = round(duration * 0.05, 2)  # voorbeeldtarief
                return s
        raise Exception("No active session found for this vehicle.")

    #Alle sessies ophalen
    def get_all_sessions(self) -> List[Session]:
        return self.session_list

    #Alle actieve sessies ophalen
    def get_active_sessions(self) -> List[Session]:
        return [s for s in self.session_list if s["stopped"] is None]


    def find_sessions(
        self,
        parking_lot_id: int = None,
        vehicle_id: int = None,
        user_id: int = None,
        session_id: int = None,
        license_plate: str = None,
        payment_status: str = None,
        active_only: bool = False,
    ) -> list[Session]:

        filtered_sessions = self.session_list.copy()

        if parking_lot_id is not None:
            filtered_sessions = [
                s for s in filtered_sessions if s.parking_lot_id == parking_lot_id
            ]

        if vehicle_id is not None:
            filtered_sessions = [
                s for s in filtered_sessions if s.vehicle_id == vehicle_id
            ]

        if user_id is not None:
            filtered_sessions = [s for s in filtered_sessions if s.user_id == user_id]

        if session_id is not None:
            filtered_sessions = [s for s in filtered_sessions if s.id == session_id]

        if license_plate is not None:
            filtered_sessions = [
                s for s in filtered_sessions if s.license_plate == license_plate
            ]

        if payment_status is not None:
            filtered_sessions = [
                s for s in filtered_sessions if s.payment_status == payment_status
            ]

        if active_only:
            filtered_sessions = [s for s in filtered_sessions if s.end_time is None]

        return filtered_sessions

    def update_session(self, session_id: int, updated_session: Session) -> bool:
        for index, session in enumerate(self.session_list):
            if session.id == session_id:
                self.session_list[index] = updated_session
                return True
        return False

    def delete_session(self, session_id: int) -> bool:
        for index, session in enumerate(self.session_list):
            if session.id == session_id:
                self.session_list.pop(index)
                return True
        return False
