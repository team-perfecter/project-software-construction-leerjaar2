import psycopg2
from api.datatypes.reservation import Reservation, ReservationCreate


class Reservation_model:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    def get_all_reservations(self) -> list[Reservation]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM reservations")
        return cursor.fetchall()
    
    def get_reservation_by_id(self, reservation_id) -> Reservation | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id = %s", (reservation_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def create_reservation(self, reservation_data: dict) -> int:
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO reservations (vehicle_id, user_id, parking_lot_id, start_time, end_time, status, cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (
            reservation_data["vehicle_id"],
            reservation_data["user_id"],
            reservation_data["parking_lot_id"],
            reservation_data["start_time"],
            reservation_data["end_time"],
            reservation_data["status"],
            reservation_data.get("cost", 0)
        ))
        self.connection.commit()
        return cursor.fetchone()[0]

    def get_reservation_by_vehicle(self, vehicle_id: int) -> list[dict]:
        """Get all reservations for a specific vehicle"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM reservations 
            WHERE vehicle_id = %s
            ORDER BY start_time DESC
        """, (vehicle_id,))
        
        columns = [desc[0] for desc in cursor.description]
        reservations = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            reservations.append(row_dict)
        
        return reservations

    def delete_reservation(self, reservation_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = %s RETURNING id;", (reservation_id,))
        deleted = cursor.fetchone()
        self.connection.commit()
        return deleted is not None
