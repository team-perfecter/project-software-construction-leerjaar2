from datatypes.parking_lot import Parking_lot

#eventually the database queries / JSON write/read will be here.

class Parking_lot_storage:
    def __init__(self):
        self.parking_lot_list: list[Parking_lot] = []

    def get_all_parking_lots(self) -> list[Parking_lot]:
        return self.parking_lot_list
    
    def get_parking_lot_by_id(self, parking_lot_id) -> Parking_lot | None:
        for parking_lot in self.parking_lot_list:
            if parking_lot.id == parking_lot_id:
                return parking_lot
        return None
    
    def post_parking_lot(self, parking_lot: Parking_lot) -> None:
        self.parking_lot_list.append(parking_lot)