from datetime import datetime
import os

import psycopg2
import json
import logging

from api.utilities.Hasher import hash_string

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class DataConverter:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password",
        )

        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    def read_data(self, filename):
        filepath = os.path.join(self.script_dir, 'data', f'{filename}.json')
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        with open(filepath, 'r') as f:
            data = json.load(f)
        if data:
            return data
        else:
            logging.info("No data found")
            return None

    def insert_user(self, data):
        cursor = self.connection.cursor()
        for user in data:
            # Count existing users with the same username
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (user["username"],))
            count = cursor.fetchone()[0]

            is_active = count == 0  # First occurrence = active=True, duplicates=False

            cursor.execute("""
                           INSERT INTO users (id, username, password, name, email, phone, birth_year, active, old_hash)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """, (
                               user["id"],
                               user["username"],
                               user["password"],
                               user["name"],
                               user["email"],
                               user["phone"],
                               user["birth_year"],
                               is_active,
                               True
                           ))
        self.connection.commit()
        cursor.close()

    def add_super_admin(self):
        # Check for superadmin
        cur = self.connection.cursor()
        cur.execute("SELECT id FROM users WHERE role = 'superadmin' LIMIT 1;")
        exists = cur.fetchone()

        if not exists:
            try:
                hashed_pw = hash_string("admin123")

                cur.execute("""
                            INSERT INTO users (username, password, name, email, role)
                            VALUES ('superadmin', %s, 'Super Admin', 'super@admin.com', 'superadmin');
                            """, (hashed_pw,))

                print("Default superadmin created.")
                self.connection.commit()

            except Exception as e:
                self.connection.rollback()
                print("Failed to create superadmin:", e)
        else:
            print("Superadmin already exists.")

    def insert_vehicle(self, data):
        cursor = self.connection.cursor()

        for vehicle in data:
            try:
                created_at = datetime.strptime(vehicle["created_at"], "%Y-%m-%d").date()
                user_id = vehicle.get("user_id")
                cursor.execute("""
                               INSERT INTO vehicles (user_id, license_plate, make, model, color, year, created_at)
                               VALUES (%s, %s, %s, %s, %s, %s, %s)
                               """, (
                                   user_id,
                                   vehicle["license_plate"],
                                   vehicle["make"],
                                   vehicle["model"],
                                   vehicle["color"],
                                   vehicle["year"],
                                   created_at
                               ))
            except Exception as e:
                logging.error(f"Failed to insert vehicle {vehicle}: {e}")
        self.connection.commit()
        cursor.close()

    def insert_parking_lots(self, data):
        cursor = self.connection.cursor()

        for key, lot in data.items():
            try:
                created_at = datetime.strptime(lot["created_at"], "%Y-%m-%d").date()

                lat = lot.get("coordinates", {}).get("lat")
                lng = lot.get("coordinates", {}).get("lng")

                cursor.execute("""
                               INSERT INTO parking_lots
                               (id, name, location, address, capacity, reserved, tariff, daytariff, created_at, lat,
                                lng)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                               """, (
                                   lot["id"],
                                   lot["name"],
                                   lot["location"],
                                   lot["address"],
                                   lot["capacity"],
                                   lot["reserved"],
                                   lot["tariff"],
                                   lot["daytariff"],
                                   created_at,
                                   lat,
                                   lng
                               ))

            except Exception as e:
                logging.error(f"Failed to insert parking lot {lot}: {e}")

        self.connection.commit()
        cursor.close()


    def convert(self):
        user_data = self.read_data('users')
        if not user_data:
            logging.info("No users data found, aborting conversion")
            return
        logging.info("Read the user data from json")
        self.insert_user(user_data)
        logging.info("Users successfully inserted")

        vehicle_data = self.read_data('vehicles')
        if not vehicle_data:
            logging.info("No vehicle data found, aborting conversion")
            return
        self.insert_vehicle(vehicle_data)
        logging.info("Vehicles successfully inserted")

        parking_lot_data = self.read_data('parking-lots')
        if not parking_lot_data:
            logging.info("No parking lots data found, aborting conversion")
            return
        self.insert_parking_lots(parking_lot_data)



