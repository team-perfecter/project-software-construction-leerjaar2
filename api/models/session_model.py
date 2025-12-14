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
    def create_session(self, parking_lot_id: int, user_id: int, vehicle_id: int) -> Session | None:
        cursor = self.connection.cursor()

        # Controleer of dit voertuig al actief is
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

    # Sessie stoppen (wanneer voertuig vertrekt)
    def stop_session(self, session: Session):

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

    # Alle sessies ophalen
    def get_all_sessions(self) -> list[Session]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions;")
        return self.map_to_session(cursor)

    # Alleen actieve sessies ophalen
    def get_active_sessions(self) -> list[Session]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE stopped IS NULL;")
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

    def get_vehicle_sessions(self, vehicle_id: int):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM sessions WHERE vehicle_id = %s AND stopped IS NULL;
        """, (vehicle_id,))
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description]

        result = [
            {
                col: (val.isoformat() if isinstance(val, datetime) else val)
                for col, val in zip(columns, row)
            }
            for row in rows
        ]

        return result

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
