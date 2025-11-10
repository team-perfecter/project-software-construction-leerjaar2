from datetime import date

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="database",
    user="user",
    password="password",
)

cur = conn.cursor()


# Data for the new user
username = "johndoe"
password = "securepassword"   # For production, hash passwords!
name = "John Doe"
email = "john@example.com"
phone = "1234567890"
role = "admin"
created_at = date.today()
birth_year = 1990
active = True

# Insert query (use placeholders to prevent SQL injection)
cur.execute("""
    INSERT INTO users (username, password, name, email, phone, role, created_at, birth_year, active)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
""", (username, password, name, email, phone, role, created_at, birth_year, active))

user_id = cur.fetchone()[0]
conn.commit()

print(f"user with id {user_id} created")

cur.close()
conn.close()