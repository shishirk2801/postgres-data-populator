import os
from psycopg2 import pool
import aiopg

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "test_db"),
    "user": os.getenv("DB_USER", "user"),
    "password": os.getenv("DB_PASS", "password")
}

connection_pool = pool.SimpleConnectionPool(
    1, 20, **DB_CONFIG
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)

async def get_async_connection():
    dsn = f"dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']} host={DB_CONFIG['host']} port={DB_CONFIG['port']}"
    return await aiopg.connect(dsn)

async def release_async_connection(conn):
    conn.close()