import psycopg2

database_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="database",
    user="user",
    password="password",
)