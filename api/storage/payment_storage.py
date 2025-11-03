from api.datatypes.payment import Payment

#eventually the database queries / JSON write/read will be here.

class Payment_storage:
    def __init__(self):
        self.payment_list: list[Payment] = []

    def get_all_payments(self) -> list[Payment]:
        return self.payment_list
    
    def get_payment_by_id(self, payment_id) -> Payment | None:
        for payment in self.payment_list:
            if payment.id == payment_id:
                return payment
        return None
    
    def post_payment(self, payment: Payment) -> None:
        self.payment_list.append(payment)

    def get_payments_by_user(self, user_id: int) -> list[Payment]:
        result: list[Payment] = []
        for payment in self.payment_list:
            if payment.user_id == user_id:
                result.append(payment)
        return result
    
    def get_open_payments_by_user(self, user_id: int) -> list[Payment]:
        result: list[Payment] = []
        for payment in self.payment_list:
            if payment.user_id == user_id and payment.completed_at is None:
                result.append(payment)
        return result
