from datetime import datetime
from api.datatypes.session import Session


class Session_storage:
    def __init__(self):
        self.session_list: list[Session] = []

    def start_session(self, session: Session) -> None:
        self.session_list.append(session)

    def get_sessions(self) -> list[Session]:
        return self.session_list

    def get_all_sessions_by_id(
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
