import os
from dotenv import load_dotenv

load_dotenv(".env")

db_config = {
    "min_conn": int(os.getenv("DB_POOL_MIN_CONN", 1)),
    "max_conn": int(os.getenv("DB_POOL_MAX_CONN", 10)),
    "db_user": os.getenv("DB_USER"),
    "db_password": os.getenv("DB_PASSWORD"),
    "db_host": os.getenv("DB_HOST"),
    "db_port": os.getenv("DB_PORT"),
    "db_name": os.getenv("DB_NAME"),
}
