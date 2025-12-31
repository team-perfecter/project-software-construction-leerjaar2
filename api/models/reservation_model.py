import psycopg2

from api.datatypes.reservation import ReservationCreate, Reservation


#eventually the database queries / JSON write/read will be here.

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
        return cursor.fetchone()


    def create_reservation(self, reservation: ReservationCreate, user_id, payment_id, cost) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO reservations (vehicle_id, user_id, parking_lot_id, payment_id, start_time, end_time, cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (reservation.vehicle_id, user_id, reservation.parking_lot_id, payment_id, reservation.start_time, reservation.end_time, cost))
        self.connection.commit()
        return cursor.fetchone()[0]


#     def get_reservation_by_vehicle(self, vehicle_id: int) -> list[Reservation]:
#         cursor = self.connection.cursor()
#         cursor.execute("SELECT * FROM reservations WHERE vehicle_id = %s", (vehicle_id,))
#         return cursor.fetchall()


    def link_payment_to_reservation(self, reservation_id: int, payment_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE reservations
            SET payment_id = %s
            WHERE id = %s
            RETURNING id;
        """, (payment_id, reservation_id))
        updated = cursor.fetchone()
        self.connection.commit()
        return updated is not None


    def delete_reservation(self, reservation_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = %s RETURNING id;", (reservation_id,))
        deleted = cursor.fetchone()
        self.connection.commit()
        return deleted is not None
