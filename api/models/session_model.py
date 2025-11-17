import psycopg2
from datetime import datetime
from api.datatypes.session import Session


class SessionModel:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    # Nieuwe sessie starten
    def create_session(self, parking_lot_id: int, user_id: int, vehicle_id: int) -> Session:
        cursor = self.connection.cursor()

        # Controleer of dit voertuig al actief is
        cursor.execute("""
            SELECT * FROM sessions WHERE vehicle_id = %s AND stopped IS NULL;
        """, (vehicle_id,))
        if cursor.fetchone():
            raise Exception("Vehicle already has an active session.")

        started = datetime.now()

        cursor.execute("""
            INSERT INTO sessions (parking_lot_id, user_id, vehicle_id, started)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
        """, (parking_lot_id, user_id, vehicle_id, started))

        self.connection.commit()
        session_list = self.map_to_session(cursor)
        return session_list[0] if len(session_list) > 0 else None

    # Sessie stoppen (wanneer voertuig vertrekt)
    def stop_session(self, vehicle_id: int) -> Session | None:
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT * FROM sessions WHERE vehicle_id = %s AND stopped IS NULL;
        """, (vehicle_id,))
        result = cursor.fetchone()

        if not result:
            raise Exception("No active session found for this vehicle.")

        columns = [desc[0] for desc in cursor.description]
        active_session = dict(zip(columns, result))

        stopped = datetime.now()
        duration_minutes = int((stopped - active_session["started"]).total_seconds() / 60)
        cost = round(duration_minutes * 0.05, 2)

        cursor.execute("""
            UPDATE sessions
            SET stopped = %s,
                duration_minutes = %s,
                cost = %s
            WHERE id = %s
            RETURNING *;
        """, (stopped, duration_minutes, cost, active_session["id"]))

        self.connection.commit()
        session_list = self.map_to_session(cursor)
        return session_list[0] if len(session_list) > 0 else None

    # Alle sessies ophalen
    def get_all_sessions(self) -> list[Session]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions;")
        return self.map_to_session(cursor)

    # Alleen actieve sessies ophalen
    def get_active_sessions(self) -> list[Session]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE stopped IS NULL;")
        return self.map_to_session(cursor)

    # Sessie zoeken op ID
    def get_session_by_id(self, session_id: int) -> Session | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = %s;", (session_id,))
        session_list = self.map_to_session(cursor)
        return session_list[0] if len(session_list) > 0 else None

    # Helperfunctie om DB-rijen om te zetten naar Session objecten
    def map_to_session(self, cursor):
        columns = [desc[0] for desc in cursor.description]
        return [Session(**dict(zip(columns, row))) for row in cursor.fetchall()]
