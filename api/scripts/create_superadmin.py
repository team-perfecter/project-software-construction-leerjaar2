from api.utilities.Hasher import hash_string
import psycopg2

conn = psycopg2.connect(
    host="db",
    port=5432,
    database="database",
    user="user",
    password="password"
)
cur = conn.cursor()

cur.execute("SELECT id FROM users WHERE role='superadmin' LIMIT 1;")
exists = cur.fetchone()

if not exists:
    hashed_pw = hash_string("admin123")
    cur.execute("""
        INSERT INTO users (username, password, name, email, role)
        VALUES ('superadmin', %s, 'Super Admin', 'super@admin.com', 'superadmin');
    """, (hashed_pw,))
    conn.commit()
    print("Default superadmin created.")
else:
    print("Superadmin already exists.")

cur.close()
conn.close()
