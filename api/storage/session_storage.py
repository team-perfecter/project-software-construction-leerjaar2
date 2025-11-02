from datetime import datetime
from api.datatypes.session import Session


class Session_storage:
    def __init__(self):
        self.session_list: list[Session] = []

    def add_session(self, session: Session):
        self.session_list.append(session)

    def remove_session(self, session: Session):
        self.session_list.remove(session)

    def get_sessions(self) -> list[Session]:
        return self.session_list