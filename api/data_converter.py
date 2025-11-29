from datetime import datetime
import os

import psycopg2
import json
import logging

from psycopg2.extras import execute_values

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

    def read_session_data(self):
        pdata = {}
        for i in range(1, 1500):
            filepath = os.path.join(self.script_dir, 'data/pdata', f'p{i}-sessions.json')
            if not os.path.exists(filepath):
                logging.warning(f"File not found: {filepath}")
                continue
            with open(filepath, 'r') as f:
                data = json.load(f)

            if isinstance(data, dict):
                pdata.update(data)
            else:
                logging.error(f"Unexpected data type in {filepath}: {type(data).__name__}, skipping")
                continue
        return pdata

    def insert_user(self, data):
        cursor = self.connection.cursor()
        for user in data:
            # Count existing users with the same username
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (user["username"],))
            count = cursor.fetchone()[0]

            is_active = count == 0  # First occurrence = active=True, duplicates=False

            cursor.execute("""
                           INSERT INTO users (username, password, name, email, phone, birth_year, active, old_hash)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                           """, (
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
                               (name, location, address, capacity, reserved, tariff, daytariff, created_at, lat,
                                lng)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                               """, (
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

    from psycopg2.extras import execute_values
    from datetime import datetime
    import logging

    def insert_payment(self, data, batch_size=10000):
        cursor = self.connection.cursor()

        # Preload users into a dictionary
        cursor.execute("SELECT id, username FROM users")
        user_map = {username: user_id for user_id, username in cursor.fetchall()}

        insert_sql = """
                     INSERT INTO payments (user_id, transaction, amount, completed, hash, method, issuer, bank, date) \
                     VALUES %s \
                     """

        batch = []

        for payment in data:
            try:
                username = payment.get("initiator")
                user_id = user_map.get(username)

                if username and user_id is None:
                    logging.warning(
                        f"Payment for username '{username}' could not be uniquely matched. Assigning user_id=NULL."
                    )

                t_data = payment.get("t_data", {})
                method = t_data.get("method")
                issuer = t_data.get("issuer")
                bank = t_data.get("bank")
                amount = float(payment.get("amount", 0))
                completed = payment.get("completed") not in [None, "", False]

                # Parse the date from t_data["date"]
                date_str = t_data.get("date")
                if date_str:
                    try:
                        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        logging.warning(f"Invalid date format for payment {payment.get('transaction')}, using NOW()")
                        date = datetime.now()
                else:
                    date = datetime.now()

                batch.append((
                    user_id,
                    payment.get("transaction"),
                    amount,
                    completed,
                    payment.get("hash"),
                    method,
                    issuer,
                    bank,
                    date
                ))

                # Insert in batches
                if len(batch) >= batch_size:
                    execute_values(cursor, insert_sql, batch)
                    batch.clear()

            except Exception as e:
                logging.error(f"Failed to process payment {payment}: {e}")

        # Insert remaining records
        if batch:
            execute_values(cursor, insert_sql, batch)

        self.connection.commit()
        cursor.close()
        logging.info("Payments successfully inserted")

    def insert_reservations(self, data):
        cursor = self.connection.cursor()

        for res in data:
            try:
                start_time = datetime.strptime(res.get("start_time"), "%Y-%m-%dT%H:%M:%SZ")
                end_time = datetime.strptime(res.get("end_time"), "%Y-%m-%dT%H:%M:%SZ")
                created_at = datetime.strptime(res.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")

                cursor.execute("""
                               INSERT INTO reservations (vehicle_id,
                                                         user_id,
                                                         parking_lot_id,
                                                         start_time,
                                                         end_time,
                                                         status,
                                                         created_at,
                                                         cost)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                               """, (
                                   res.get("vehicle_id"),
                                   res.get("user_id"),
                                   res.get("parking_lot_id"),
                                   start_time,
                                   end_time,
                                   res.get("status"),
                                   created_at,
                                   res.get("cost")
                               ))

            except Exception as e:
                logging.error(f"Failed to insert reservation {res}: {e}")

        self.connection.commit()
        cursor.close()


    def insert_sessions(self, data):
        cursor = self.connection.cursor()

        # Preload users and vehicles
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        user_counts = {}
        for user_id, username in users:
            if username in user_counts:
                user_counts[username].append(user_id)
            else:
                user_counts[username] = [user_id]

        cursor.execute("SELECT id, license_plate FROM vehicles")
        vehicle_map = {licence_plate.strip().upper(): vehicle_id for vehicle_id, licence_plate in cursor.fetchall()}

        for session_id, session in data.items():
            try:
                # Parse timestamps
                started = datetime.strptime(session.get("started"), "%Y-%m-%dT%H:%M:%SZ") if session.get(
                    "started") else None
                stopped = datetime.strptime(session.get("stopped"), "%Y-%m-%dT%H:%M:%SZ") if session.get(
                    "stopped") else None

                # Resolve user_id
                username = session.get("user")
                user_ids = user_counts.get(username, [])
                if len(user_ids) == 1:
                    user_id = user_ids[0]
                else:
                    user_id = None
                    if len(user_ids) > 1:
                        logging.warning(f"Multiple users found for username '{username}', leaving user_id NULL")
                    elif len(user_ids) == 0:
                        logging.warning(f"No user found for username '{username}'")

                # Resolve vehicle_id
                license_plate = session.get("licenseplate")
                vehicle_id = vehicle_map.get(license_plate.strip().upper()) if license_plate else None
                if vehicle_id is None:
                    logging.warning(f"No vehicle found for license plate '{license_plate}'")

                cursor.execute("""
                               INSERT INTO sessions (parking_lot_id,
                                                     payment_id,
                                                     user_id,
                                                     vehicle_id,
                                                     started,
                                                     stopped,
                                                     duration_minutes,
                                                     cost)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                               """, (
                                   session.get("parking_lot_id"),
                                   None,  # No payment info in sessions JSON
                                   user_id,
                                   vehicle_id,
                                   started,
                                   stopped,
                                   session.get("duration_minutes"),
                                   session.get("cost")
                               ))

            except Exception as e:
                logging.error(f"Failed to insert session {session_id}: {e}")

        self.connection.commit()
        cursor.close()
        logging.info("Sessions successfully inserted")

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
        logging.info("Parking lots successfully inserted")

        #payment_data = self.read_data('payments')
        #if not payment_data:
        #    logging.info("No payments data found, aborting conversion")
        #    return
        #self.insert_payment(payment_data)
        #logging.info("Payments successfully inserted")

        reservation_data = self.read_data('reservations')
        if not reservation_data:
            logging.info("No reservations data found, aborting conversion")
            return
        self.insert_reservations(reservation_data)
        logging.info("Reservations successfully inserted")

        session_data = self.read_session_data()
        if not session_data:
            logging.info("No session data found, aborting conversion")
            return
        self.insert_sessions(session_data)


