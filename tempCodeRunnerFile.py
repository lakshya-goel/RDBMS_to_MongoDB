import psycopg2
from pymongo import MongoClient
from psycopg2.extras import RealDictCursor

# PostgreSQL connection
pg_conn = psycopg2.connect(
    dbname="a1",
    user="postgres",
    password="lak",
    host="localhost"
)