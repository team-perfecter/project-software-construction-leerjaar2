from datetime import datetime
from typing import List, Optional
from api.datatypes.session import Session
from api.models.session_model import SessionModel

class Session_storage:
    """Database-opslag voor parkeersessies (via psycopg2)."""

    def __init__(self):
        self.model = SessionModel()

    # Nieuwe sessie starten
    def start_session(self, vehicle_id: int, user_id: int, parking_lot_id: int = 1):
        """
        Start een nieuwe sessie in de database.
        """
        # controleer eerst of er al een actieve sessie is
        active_sessions = self.model.get_active_sessions()
        for s in active_sessions:
            if s["vehicle_id"] == vehicle_id:
                raise Exception("Vehicle already has an active session.")

        # maak nieuwe sessie aan in de DB
        session_id = self.model.start_session(parking_lot_id, user_id, vehicle_id)
        return {"message": "Session started", "session_id": session_id}

    # Actieve sessie stoppen
    def stop_session(self, vehicle_id: int):
        """
        Stop de actieve sessie van dit voertuig.
        """
        active_sessions = self.model.get_active_sessions()
        for s in active_sessions:
            if s["vehicle_id"] == vehicle_id:
                stopped_session = self.model.end_session(s["id"])
                return stopped_session

        raise Exception("No active session found for this vehicle.")

    # Alle sessies ophalen
    def get_all_sessions(self):
        return self.model.get_all_sessions()

    # Alle actieve sessies ophalen
    def get_active_sessions(self):
        return self.model.get_active_sessions()

    # Specifieke sessie zoeken
    def find_sessions(
        self,
        parking_lot_id: int = None,
        vehicle_id: int = None,
        user_id: int = None,
        session_id: int = None,
        active_only: bool = False,
    ):
        # Je kunt hier je model-functies uitbreiden later als filtering nodig is
        sessions = self.model.get_all_sessions()
        if active_only:
            sessions = [s for s in sessions if s["stopped"] is None]
        if vehicle_id:
            sessions = [s for s in sessions if s["vehicle_id"] == vehicle_id]
        if user_id:
            sessions = [s for s in sessions if s["user_id"] == user_id]
        return sessions

    def delete_session(self, session_id: int) -> bool:
        cursor = self.model.connection.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = %s;", (session_id,))
        self.model.connection.commit()
        return cursor.rowcount > 0