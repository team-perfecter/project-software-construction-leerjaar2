from datetime import datetime
from hashlib import md5
import math
import uuid
from decimal import Decimal, ROUND_HALF_UP


def calculate_price(parking_lot, session, discount_code):
    start = session.start_time
    end = session.end_time or datetime.now()

    diff = end - start
    hours = math.ceil(diff.total_seconds() / 3600)

    if diff.total_seconds() < 180:
        price = 0
    elif end.date() > start.date():
        price = float(parking_lot.daytariff) * (diff.days + 1)
    else:
        price = float(parking_lot.tariff) * hours
        if price > float(parking_lot.daytariff):
            price = float(parking_lot.daytariff)
    if discount_code is not None: 
        if discount_code["discount_type"] == "fixed":
            price -= discount_code["discount_value"]
        else:
            price *= (1 - discount_code["discount_value"] / 100)
    if price < 0:
        price = 0
    price = Decimal(str(price))
    price = price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return price


def generate_payment_hash(sid, licenseplate):
    return md5(str(sid + licenseplate).encode("utf-8")).hexdigest()


def generate_transaction_validation_hash():
    return str(uuid.uuid4())


# def check_payment_amount(hash):
#     payments = load_payment_data()
#     total = 0

#     for payment in payments:
#         if payment["transaction"] == hash:
#             total += payment["amount"]
#     return total
