from datetime import datetime
from hashlib import md5
import math
import uuid


def calculate_price(parking_lot, obj):
    if hasattr(obj, "started"):
        start = obj.started
        end = obj.stopped or datetime.now()
    elif hasattr(obj, "start_time"):
        start = obj.start_time
        end = obj.end_time or datetime.now()
    else:
        raise ValueError("Object must be a Session or Reservation with appropriate time fields.")

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
