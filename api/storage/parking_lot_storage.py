from datetime import date
from api.datatypes.parking_lot import Parking_lot

# eventually the database queries / JSON write/read will be here.


class Parking_lot_storage:
    def __init__(self):
        self.parking_lot_list: list[Parking_lot] = [
            Parking_lot(
                id=1,
                name="Bedrijventerrein Almere Parkeergarage",
                location="Industrial Zone",
                address="Schanssingel 337, 2421 BS Almere",
                capacity=335,
                reserved=77,
                tariff=1.9,
                daytariff=11.0,
                created_at=date(2020, 3, 25),
                lat=52.3133,
                lng=5.2234,
            ),
            Parking_lot(
                id=2,
                name="Centrum Parkeergarage",
                location="City Center",
                address="Hoofdstraat 123, 1234 AB Amsterdam",
                capacity=200,
                reserved=45,
                tariff=2.5,
                daytariff=15.0,
                created_at=date(2021, 5, 10),
                lat=52.3676,
                lng=4.9041,
            ),
        ]

    def get_all_parking_lots(self) -> list[Parking_lot]:
        return self.parking_lot_list

    def get_parking_lot_by_id(self, parking_lot_id) -> Parking_lot | None:
        for parking_lot in self.parking_lot_list:
            if parking_lot.id == parking_lot_id:
                return parking_lot
        return None

    def post_parking_lot(self, parking_lot: Parking_lot) -> None:
        self.parking_lot_list.append(parking_lot)

    def delete_parking_lot(self, parking_lot_id: int) -> bool:
        for index, parking_lot in enumerate(self.parking_lot_list):
            if parking_lot.id == parking_lot_id:
                self.parking_lot_list.pop(index)
                return True
        return False
