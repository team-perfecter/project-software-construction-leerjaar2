from datetime import datetime
from typing import List, Optional, Dict, Any


class Session_storage:
    """In-memory opslag voor parkeersessies (testversie, zonder database)."""

    def __init__(self):
        #Tijdelijke opslag van sessies
        self.session_list: List[Dict[str, Any]] = []

    #Nieuwe sessie starten
    def start_session(self, vehicle_id: int, user_id: int, parking_lot_id: int = 1) -> Dict[str, Any]:
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
    def stop_session(self, vehicle_id: int) -> Dict[str, Any]:
        for s in self.session_list:
            if s["vehicle_id"] == vehicle_id and s["stopped"] is None:
                s["stopped"] = datetime.now()
                duration = (s["stopped"] - s["started"]).total_seconds() / 60
                s["duration_minutes"] = int(duration)
                s["cost"] = round(duration * 0.05, 2)  # voorbeeldtarief
                return s
        raise Exception("No active session found for this vehicle.")

    #Alle sessies ophalen
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        return self.session_list

    #Alle actieve sessies ophalen
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        return [s for s in self.session_list if s["stopped"] is None]

    #Één sessie zoeken op ID
    def get_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        for s in self.session_list:
            if s["id"] == session_id:
                return s
        return None