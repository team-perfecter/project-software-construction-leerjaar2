# import psycopg2
# from api.datatypes.reservation import Reservation

# #eventually the database queries / JSON write/read will be here.

# class Reservation_model:
#     def __init__(self):
#         self.connection = psycopg2.connect(
#             host="db",
#             port=5432,
#             database="database",
#             user="user",
#             password="password",
#         )

#     def get_all_reservations(self) -> list[Reservation]:
#         cursor = self.connection.cursor()
#         cursor.execute("SELECT * FROM reservations")
#         return cursor.fetchall()
    
#     def get_reservation_by_id(self, reservation_id) -> Reservation | None:
#         cursor = self.connection.cursor()
#         cursor.execute("SELECT * FROM reservations WHERE id = %s", (reservation_id,))
#         return cursor.fetchall()
    
#     def create_reservation(self, reservation: Reservation) -> None:
#         cursor = self.connection.cursor()
#         cursor.execute("""
#             INSERT INTO vehicles (user_id, license_plate, make, model, color, year)
#             VALUES (%s, %s, %s, %s, %s, %s)
#         """, (user_id,))

#     def get_reservation_by_vehicle(self, vehicle_id: int) -> list[Reservation]:
#         cursor = self.connection.cursor()
#         cursor.execute("SELECT * FROM reservations WHERE vehicle_id = %s", (vehicle_id,))
#         return cursor.fetchall()
