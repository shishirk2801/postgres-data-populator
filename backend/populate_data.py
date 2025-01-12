import os
from faker import Faker
from tqdm import tqdm
from backend.db import get_connection, release_connection

conn = get_connection()
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
release_connection(conn)
print("Database population completed!")
