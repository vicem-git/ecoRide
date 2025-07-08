import time
from flask import Flask, request
from psycopg_pool import ConnectionPool
import os
import sys
from . import db_store
from dotenv import load_dotenv


load_dotenv("../.env")

app = Flask(__name__)

pool = ConnectionPool(
    conninfo=f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    min_size=1,
    max_size=10,  # adjust for your app’s needs
    timeout=30,  # seconds to wait for a connection
)


@app.route("/api/time")
def get_current_time():
    return {"time": time.time()}


@app.route("/api/health")
def health_check():
    with pool.connection() as conn:
        result = db_store.crud.test_connection(conn)
    return {"status": "healthy" if result else "unhealthy"}
