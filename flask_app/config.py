import os
from dotenv import load_dotenv
from datetime import timedelta

# load_dotenv(".env")
 
class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    MAIL_API_URL = os.getenv("MAIL_API_URL", "")
    MAIL_API_KEY = os.getenv("MAIL_API_KEY", "")
    APP_ADMIN = os.getenv("APP_ADMIN", "")
    MAIL_POSTMASTER = os.getenv("MAIL_POSTMASTER", "")

    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_NAME = "session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB
    MAX_FORM_MEMORY_SIZE = 300 * 1024     # default is fine
    MAX_FORM_PARTS = 100


db_config = {
    "min_conn": int(os.getenv("DB_POOL_MIN_CONN", 1)),
    "max_conn": int(os.getenv("DB_POOL_MAX_CONN", 10)),
    "db_user": os.getenv("POSTGRES_USER"),
    "db_password": os.getenv("POSTGRES_PASS"),
    "db_host": os.getenv("POSTGRES_HOST"),
    "db_name": os.getenv("POSTGRES_DB"),
}

mongo_config = {
    "mdb_user": os.getenv("MONGO_USER"),
    "mdb_pw": os.getenv("MONGO_PASS"),
    "mdb_host": os.getenv("MONGO_HOST", "mongo"),
    "mdb_db": os.getenv("MONGO_DB", "mongo_ecoride"),
}

