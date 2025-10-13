import pytest
from fastapi.testclient import TestClient
from ../../app import app

'''
reservations will be in a seperate class. the input of this class will be the authorization token of the user.
each endpoint will check if the token is valid. if not valid, return 401
the validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.
post_reservation() is a function that posts a function to the database. 
retrieve all reservations where the parking lot or vehicle is the same as the reservation a user is trying to create
check if there is any overlap between either the parking lot or the vehicle
return an error if there is any overlap

'''

client = TestClient(app)

reservations: list = []

def insert_reservation(reservation):
    reservations.append(reservation)

def get_fake_reservations(rid: int):
    result = None
    for res in reservations:
        if res["id"] == rid:
            result = res
    return result

'''
Test creating a new reservation when a user is authorized.
'''


'''
Test creating a new reservation when a user is not authorized.
'''


'''
Test creating a new reservation when a user has not filled in all data
'''

'''
Test creating a new reservation when a parking lot does not exist
'''

'''
Test creating a new reservation when a parking lot already has a reservation
'''

'''
Test creating a new reservation when a parking lot already has a car parked
'''

'''
Test creating a new reservation when a vehicle already has a reservation
'''

'''
Test creating a new reservation when a vehicle is already parked
'''