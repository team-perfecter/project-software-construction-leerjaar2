"""
This file contains all queries related to sessions.
"""

import psycopg2
from datetime import datetime
from api.datatypes.session import Session


class SessionModel:
    """
    Handles all database operations related to parking sessions.
    """

    def __init__(self):
        """
        Initialize a new SessionModel instance and connect to the database.
        """
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    def create_session(self, parking_lot_id: int, user_id: int, vehicle_id: int) -> Session | None:
        """
        Start a new parking session for a vehicle if it does not already have an active session.

        Args:
            parking_lot_id (int): The ID of the parking lot.
            user_id (int): The ID of the user.
            vehicle_id (int): The ID of the vehicle.

        Returns:
            Session | None: The created Session object if successful, None if the vehicle already has an active session.
        """
        cursor = self.connection.cursor()

        # Check if the vehicle already has an active session
        cursor.execute("""
            SELECT * FROM sessions WHERE vehicle_id = %s AND stopped IS NULL;
        """, (vehicle_id,))
        if cursor.fetchone():
            print("Vehicle already has an active session.")
            return None

        cursor.execute("""
            INSERT INTO sessions (parking_lot_id, user_id, vehicle_id)
            VALUES (%s, %s, %s)
            RETURNING *;
        """, (parking_lot_id, user_id, vehicle_id))

        self.connection.commit()
        return self.map_to_session(cursor)[0]

    def stop_session(self, session: Session):
        """
        Stop an active session and calculate its duration and cost.

        Args:
            session (Session): The Session object representing the active session.

        Returns:
            dict: A dictionary representation of the updated session with stopped time, duration, and cost.
        """
        stopped = datetime.now()
        duration_minutes = int((stopped - session.started).total_seconds() / 60)
        cost = round(duration_minutes * 0.05, 2) + 1

        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE sessions
            SET stopped = %s,
                duration_minutes = %s,
                cost = %s
            WHERE id = %s
            RETURNING *;
        """, (stopped, duration_minutes, cost, session.id,))

        self.connection.commit()

        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

    def get_all_sessions(self) -> list[Session]:
        """
        Retrieve all sessions from the database.

        Returns:
            list[Session]: A list of all Session objects.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions;")
        return self.map_to_session(cursor)

    def get_active_sessions(self) -> list[Session]:
        """
        Retrieve all currently active sessions (not stopped).

        Returns:
            list[Session]: A list of active Session objects.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE stopped IS NULL;")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result

    def get_session_by_id(self, session_id: int) -> Session | None:
        """
        Retrieve a session by its ID.

        Args:
            session_id (int): The ID of the session.

        Returns:
            Session | None: The Session object if found, otherwise None.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = %s;", (session_id,))
        session_list = self.map_to_session(cursor)
        return session_list[0] if session_list else None

    def get_all_sessions_by_id(self, parking_lot_id: int, vehicle_id: int):
        """
        Retrieve all sessions for a specific parking lot and vehicle.

        Args:
            parking_lot_id (int): The ID of the parking lot.
            vehicle_id (int): The ID of the vehicle.

        Returns:
            Session | None: The most recent session if found, otherwise None.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE parking_lot_id = %s AND vehicle_id = %s;",
                       (parking_lot_id, vehicle_id,))
        session_list = self.map_to_session(cursor)
        return session_list[0] if session_list else None

    def get_vehicle_sessions(self, vehicle_id: int):
        """
        Retrieve all active sessions for a specific vehicle.

        Args:
            vehicle_id (int): The ID of the vehicle.

        Returns:
            list[dict]: A list of dictionaries representing each active session.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM sessions WHERE vehicle_id = %s AND stopped IS NULL;
        """, (vehicle_id,))
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description]

        result = [
            {col: (val.isoformat() if isinstance(val, datetime) else val)
             for col, val in zip(columns, row)}
            for row in rows
        ]
        return result

    def map_to_session(self, cursor) -> list[Session]:
        """
        Helper function to map database rows to Session objects.

        Args:
            cursor: The database cursor after executing a query.

        Returns:
            list[Session]: List of Session objects.
        """
        columns = [desc[0] for desc in cursor.description]
        sessions = []
        for row in cursor.fetchall():
            print(row)
            row_dict = dict(zip(columns, row))
            try:
                sessions.append(Session.parse_obj(row_dict))  # aliases are respected
            except Exception as e:
                print("Failed to map row to Session:", row_dict, e)
        return sessions
