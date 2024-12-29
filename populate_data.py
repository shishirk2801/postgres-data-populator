import os
import psycopg2
from faker import Faker
from tqdm import tqdm

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "test_db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")

conn = psycopg2.connect(
    host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
)
cursor = conn.cursor()

fake = Faker()
rows_to_insert = 1_000_000
batch_size = 10_000

for _ in tqdm(range(0, rows_to_insert, batch_size)):
    data = [
        (
            fake.text(max_nb_chars=20),
            fake.text(max_nb_chars=20),
            fake.text(max_nb_chars=20),
            fake.text(max_nb_chars=20),
            fake.text(max_nb_chars=20),
            fake.text(max_nb_chars=20),
            fake.text(max_nb_chars=20),
            fake.text(max_nb_chars=20),
            fake.text(max_nb_chars=20),
            fake.text(max_nb_chars=20),
        )
        for _ in range(batch_size)
    ]
    args_str = ",".join(
        cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", row).decode("utf-8")
        for row in data
    )
    cursor.execute(
        f"INSERT INTO test_table (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10) VALUES {args_str}"
    )
    conn.commit()

cursor.close()
conn.close()
print("Database population completed!")
