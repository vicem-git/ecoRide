import time
from flask import Flask, request
from flask_cors import CORS
from psycopg_pool import ConnectionPool
import os
from .db_store.crud import crud_utilities, access_crud
from . import routes_bp
from dotenv import load_dotenv
import atexit


load_dotenv("../.env")

app = Flask(__name__)
CORS(app, origins="http://localhost:5173", support_credentials=True)

pool = ConnectionPool(
    conninfo=f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    min_size=1,
    max_size=10,  # adjust for your app’s needs
    timeout=30,  # seconds to wait for a connection
)

app.pool = pool
with pool.connection() as conn:
    crud_utilities.configure_conn(conn, os.getenv("DB_SCHEMA"))

    try:
        app.load_static_ids = crud_utilities.load_static_ids(conn)
        print("Static IDs loaded successfully.")
    except Exception as e:
        print(f"Error loading static IDs: {e}")
        app.load_static_ids = {}


### SHOW ME THE BLUEPRINTS
app.register_blueprint(routes_bp.access.register_bp)


@app.route("/api/time")
def get_current_time():
    return {"time": time.time()}


@app.route("/api/health")
def health_check():
    with pool.connection() as conn:
        result = crud_utilities.test_connection(conn)
    return {"status": "healthy" if result else "unhealthy"}


@atexit.register
def close_pool():
    pool.close()
