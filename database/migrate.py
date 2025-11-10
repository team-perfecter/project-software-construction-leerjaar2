import time

import psycopg2

conn = None

for i in range(10):
    try:
        conn = psycopg2.connect(
            host="db",
            port=5432,
            database="database",
            user="user",
            password="password"
        )
        print("connected to database")
        break
    except psycopg2.Error as e:
        print(e)
        time.sleep(3)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR,
    password VARCHAR,
    name VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    role VARCHAR,
    created_at DATE,
    birth_year INTEGER,
    active BOOLEAN
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
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    hash VARCHAR,
    method VARCHAR,
    issue VARCHAR,
    bank VARCHAR,
    date TIMESTAMP
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

conn.commit()
cur.close()
conn.close()

print("tables created")