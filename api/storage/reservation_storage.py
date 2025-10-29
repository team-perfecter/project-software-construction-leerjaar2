from api.datatypes.reservation import Reservation

#eventually the database queries / JSON write/read will be here.

class Reservation_storage:
    def __init__(self):
        self.reservation_list: list[Reservation] = []

    def get_all_reservations(self) -> list[Reservation]:
        return self.reservation_list
    
    def get_reservation_by_id(self, id: int) -> Reservation | None:
        for reservation in self.reservation_list:
            if reservation.id == id:
                return reservation
        return None

    def get_reservations_by_vehicle_id(self, vehicle_id: int) -> list[Reservation]:
        result: list[Reservation] = []
        for reservation in self.reservation_list:
            if reservation.vehicle_id == vehicle_id:
                result.append(reservation)
        return result
    
    def post_reservation(self, reservation: Reservation) -> None:
        self.reservation_list.append(reservation)