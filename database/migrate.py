import time
import psycopg2
import sys
import hashlib
# A function that hashes a string. use this instead of hashing inside a function somewhere else, so the hashing method can be changed when needed.
def hash_string(string: str) -> str:

    # For now passwords are stored in MD5 so there is no point in hashing with argon2.
    #argon2_hasher = PasswordHasher()
    #argon2_hashed_string = argon2_hasher.hash(string)

    MD5_hashed_string = hashlib.md5(string.encode()).hexdigest()
    return MD5_hashed_string

# Get database name from command line argument or default to "database"
db_name = sys.argv[1] if len(sys.argv) > 1 else "database"

# Determine the host based on Docker service
host_name = "db" if db_name == "database" else "test_db"

conn = None
for i in range(10):
    try:
        conn = psycopg2.connect(
            host=host_name,
            port=5432,
            database=db_name,
            user="user",
            password="password"
        )
        print(f"Connected to database '{db_name}' on host '{host_name}'")
        break
    except psycopg2.Error as e:
        print(e)
        time.sleep(3)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE,
    password VARCHAR,
    name VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    role VARCHAR DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW(),
    birth_year INTEGER,
    active BOOLEAN DEFAULT TRUE,
    old_hash BOOLEAN DEFAULT FALSE
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    license_plate VARCHAR,
    make VARCHAR,
    model VARCHAR,
    color VARCHAR,
    year INTEGER,
    created_at DATE
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS parking_lots (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    location VARCHAR,
    address VARCHAR,
    capacity INTEGER,
    reserved INTEGER,
    tariff FLOAT,
    daytariff FLOAT,
    created_at DATE,
    lat FLOAT,
    lng FLOAT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    transaction VARCHAR,
    amount FLOAT,
    completed BOOLEAN DEFAULT FALSE,
    hash VARCHAR,
    method VARCHAR,
    issuer VARCHAR,
    bank VARCHAR,
    date TIMESTAMP DEFAULT NOW()
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(id),
    user_id INTEGER REFERENCES users(id),
    parking_lot_id INTEGER REFERENCES parking_lots(id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR,
    created_at TIMESTAMP,
    cost INTEGER
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    parking_lot_id INTEGER REFERENCES parking_lots(id),
    payment_id INTEGER REFERENCES payments(id),
    user_id INTEGER REFERENCES users(id),
    vehicle_id INTEGER REFERENCES vehicles(id),
    started TIMESTAMP,
    stopped TIMESTAMP,
    duration_minutes INTEGER,
    cost FLOAT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS parking_lot_admins (
    admin_user_id INTEGER REFERENCES users(id),
    parking_lot_id INTEGER REFERENCES parking_lots(id),
    PRIMARY KEY (admin_user_id, parking_lot_id)
);
""")


conn.commit()



cur.close()
conn.close()

print("Tables created in database:", db_name)
