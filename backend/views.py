import os
import xlsxwriter
from db import get_connection, release_connection
import concurrent.futures

def generate_xlsx():
    conn = get_connection()
    cursor = conn.cursor()
    file_path = "test_table_data.xlsx"
    
    cursor.execute("SELECT * FROM test_table LIMIT 0")
    columns = [desc[0] for desc in cursor.description]
    
    print("Generating XLSX file...")
    workbook = xlsxwriter.Workbook(file_path, {'constant_memory': True})
    worksheet = workbook.add_worksheet('Sheet1')
    
    for col, header in enumerate(columns):
        worksheet.write(0, col, header)

    batch_size = 50000
    cursor.execute("SELECT COUNT(*) FROM test_table")
    total_rows = cursor.fetchone()[0]
    num_chunks = (total_rows // batch_size) + 1

    def fetch_and_write_chunk(chunk_index):
        offset = chunk_index * batch_size
        cursor.execute(f"SELECT * FROM test_table LIMIT {batch_size} OFFSET {offset}")
        rows = cursor.fetchall()
        for row in rows:
            row_num = offset + rows.index(row) + 1
            for col, value in enumerate(row):
                worksheet.write(row_num, col, value)
        print(f"Processed chunk {chunk_index + 1}/{num_chunks}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(fetch_and_write_chunk, range(num_chunks))
    
    workbook.close()
    cursor.close()
    release_connection(conn)
    
    return file_path if os.path.exists(file_path) else None