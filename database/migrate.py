import time
import psycopg2
import sys
import hashlib
# A function that hashes a string.
# use this instead of hashing inside a function somewhere else,
# so the hashing method can be changed when needed.


def hash_string(string: str) -> str:
    # argon2_hasher = PasswordHasher()
    # return argon2_hasher.hash(string)
    return hashlib.md5(string.encode()).hexdigest()


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
    username VARCHAR,
    password VARCHAR,
    name VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    role VARCHAR DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW(),
    birth_year INTEGER,
    active BOOLEAN DEFAULT TRUE,
    is_new_password BOOLEAN DEFAULT FALSE
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
    created_at TIMESTAMP DEFAULT NOW()
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
    lng FLOAT,
    status VARCHAR,
    closed_reason VARCHAR,
    closed_date DATE
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
    status VARCHAR DEFAULT 'Payment Pending',
    created_at TIMESTAMP DEFAULT NOW(),
    cost INTEGER
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    parking_lot_id INTEGER REFERENCES parking_lots(id),
    user_id INTEGER REFERENCES users(id),
    vehicle_id INTEGER REFERENCES vehicles(id),
    reservation_id INTEGER REFERENCES reservations(id),
    started TIMESTAMP DEFAULT NOW(),
    stopped TIMESTAMP,
    cost FLOAT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    parking_lot_id INTEGER REFERENCES parking_lots(id) ON DELETE CASCADE ON UPDATE CASCADE,
    reservation_id INTEGER REFERENCES reservations(id),
    session_id INTEGER REFERENCES sessions(id),
    transaction VARCHAR,
    amount FLOAT,
    completed BOOLEAN DEFAULT FALSE,
    hash VARCHAR,
    method VARCHAR,
    issuer VARCHAR,
    bank VARCHAR,
    date TIMESTAMP DEFAULT NOW(),
    refund_requested BOOLEAN DEFAULT FALSE,
    refund_accepted BOOLEAN DEFAULT FALSE,
    admin_id INTEGER REFERENCES users(id)
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

# Check for superadmin
cur.execute("SELECT id FROM users WHERE role = 'superadmin' LIMIT 1;")
exists = cur.fetchone()

if not exists:
    try:
        hashed_pw = hash_string("admin123")

        cur.execute("""
            INSERT INTO users (username, password, name, email, role)
            VALUES ('superadmin', %s, 'Super Admin',
                    'super@admin.com', 'superadmin');
        """, (hashed_pw,))

        print("Default superadmin created.")
        conn.commit()

        cur.execute("""
            INSERT INTO users (username, password, name, email, role)
            VALUES ('lotadmin', %s, 'LotAdmin', 'admin@admin.com', 'lotadmin');
        """, (hashed_pw,))

        conn.commit()
        cur.execute("""
            INSERT INTO users (username, password, name, email, role)
            VALUES ('paymentadmin', %s, 'paymentadmin',
                    'payment@admin.com', 'paymentadmin');
        """, (hashed_pw,))

        conn.commit()
        cur.execute("""
            INSERT INTO users (username, password, name, email, role)
            VALUES ('user', %s, 'testuser', 'test@user.com', 'user');
        """, (hashed_pw,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Failed to create superadmin:", e)
else:
    print("Superadmin already exists.")

cur.close()
conn.close()

print("Tables created in database:", db_name)
