import psycopg2
import os
from datetime import datetime
from api.datatypes.session import Session
import psycopg2.extras

class SessionModel:
    def __init__(self):
        if os.environ.get("TESTING") == "1":
            host = "test_db"
            database = "test_database"
        else:
            host = "db"
            database = "database"
        self.connection = psycopg2.connect(
            host=host,
            port=5432,
            database=database,
            user="user",
            password="password",
        )

    # Nieuwe sessie starten
    def create_session(self, parking_lot_id: int, user_id: int, license_plate: str, reservation_id: int) -> Session | None:
        cursor = self.connection.cursor()
        # Controleer of dit voertuig al actief is
        cursor.execute("""
            SELECT * FROM sessions WHERE license_plate = %s AND end_time IS NULL;
        """, (license_plate,))
        if cursor.fetchone():
            print("Vehicle already has an active session.")
            return None

        cursor.execute("""
            INSERT INTO sessions (parking_lot_id, user_id, license_plate, reservation_id)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
        """, (parking_lot_id, user_id, license_plate, reservation_id))

        self.connection.commit()
        return self.map_to_session(cursor)[0]

    # Sessie stoppen (wanneer voertuig vertrekt)
    def stop_session(self, session: Session, cost: float) -> Session:
        end_time = datetime.now()
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE sessions
            SET end_time = %s,
                cost = %s
            WHERE id = %s
            RETURNING *;
        """, (end_time, cost, session.id,))

        self.connection.commit()
        session_list = self.map_to_session(cursor)
        return session_list[0] if session_list else None

    # Alle sessies ophalen
    def get_all_sessions(self) -> list[Session]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions;")
        return self.map_to_session(cursor)

    # Alleen actieve sessies ophalen
    def get_active_sessions(self) -> list[Session]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE end_time IS NULL;")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result

    # Sessie zoeken op ID
    def get_session_by_id(self, session_id: int) -> Session | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = %s;", (session_id,))
        session_list = self.map_to_session(cursor)
        return session_list[0] if len(session_list) > 0 else None

    def get_all_sessions_by_id(self, lid, vehicle_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE parking_lot_id = %s AND vehicle_id = %s;", (lid, vehicle_id,))
        session_list = self.map_to_session(cursor)
        return session_list[0] if len(session_list) > 0 else None

    def get_vehicle_session(self, license_plate: str) -> Session | None:
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM sessions WHERE license_plate = %s AND end_time IS NULL;
        """, (license_plate,))
        session_list = self.map_to_session(cursor)
        return session_list[0] if session_list else None
    
    def get_session_by_reservation_id(self, reservation_id: int) -> Session | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE reservation_id = %s AND end_time IS NULL;", (reservation_id,))
        rows = cursor.fetchall()
        if not rows:
            return None
        columns = [desc[0] for desc in cursor.description]
        data = dict(zip(columns, rows[0]))
        return Session(**data)

    # Helperfunctie om DB-rijen om te zetten naar Session objecten
    def map_to_session(self, cursor) -> list[Session]:
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

    def get_session_by_license_plate(self, license_plate):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM sessions WHERE license_plate = %s AND stopped IS NULL;", (license_plate,))
        return cursor.fetchone()