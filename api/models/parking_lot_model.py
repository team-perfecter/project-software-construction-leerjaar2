import psycopg2
from api.datatypes.parking_lot import Parking_lot
from typing import List, Optional


class ParkingLotModel:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

    def get_all_parking_lots(self) -> List[Parking_lot]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM parking_lots;")
        return self.map_to_parking_lot(cursor)

    def get_parking_lot_by_id(self, lot_id: int) -> Optional[Parking_lot]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM parking_lots WHERE id = %s;", (lot_id,))
        lots = self.map_to_parking_lot(cursor)
        return lots[0] if lots else None

    def create_parking_lot(self, lot: Parking_lot) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO parking_lots 
            (name, location, address, capacity, reserved, tariff, daytariff, created_at, lat, lng)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
            (
                lot.name,
                lot.location,
                lot.address,
                lot.capacity,
                lot.reserved,
                lot.tariff,
                lot.daytariff,
                lot.created_at,
                lot.lat,
                lot.lng,
            ),
        )
        self.connection.commit()

    def update_parking_lot(self, lot_id: int, lot: Parking_lot) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE parking_lots 
            SET name = %s, location = %s, address = %s, capacity = %s, 
                reserved = %s, tariff = %s, daytariff = %s, lat = %s, lng = %s
            WHERE id = %s;
        """,
            (
                lot.name,
                lot.location,
                lot.address,
                lot.capacity,
                lot.reserved,
                lot.tariff,
                lot.daytariff,
                lot.lat,
                lot.lng,
                lot_id,
            ),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_parking_lot(self, lot_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM parking_lots WHERE id = %s;", (lot_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def map_to_parking_lot(self, cursor) -> List[Parking_lot]:
        columns = [desc[0] for desc in cursor.description]
        parking_lots = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            try:
                user = Parking_lot.parse_obj(row_dict)
                parking_lots.append(user)
            except Exception as e:
                print("Failed to map row to User:", row_dict, e)
        return parking_lots
