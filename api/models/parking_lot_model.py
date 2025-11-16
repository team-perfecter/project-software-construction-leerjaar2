import psycopg2
from api.datatypes.parking_lot import Parking_lot
from typing import List, Optional

class ParkingLotModel:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="localhost",
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
        cursor.execute("""
            INSERT INTO parking_lots 
            (name, location, address, capacity, reserved, tariff, daytariff, created_at, lat, lng)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (lot.name, lot.location, lot.address, lot.capacity, lot.reserved, 
              lot.tariff, lot.daytariff, lot.created_at, lot.lat, lot.lng))
        self.connection.commit()

    def map_to_parking_lot(self, cursor) -> List[Parking_lot]:
        columns = [desc[0] for desc in cursor.description]
        return [Parking_lot(**dict(zip(columns, row))) for row in cursor.fetchall()]