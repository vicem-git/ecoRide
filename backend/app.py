import time
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os
import sys

sys.path.insert(0, ".")

from dotenv import load_dotenv
import db_store.alchemy as alchemy
import db_store.models as models
import db_store.crud as crud

load_dotenv("../.env")

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

alchemy_db = alchemy.alchemy_db
alchemy_db.init_app(app)


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/time")
def get_current_time():
    return {"time": time.time()}


@app.route("/api/health")
def health_check():
    result = crud.test_connection()
    return {"status": "healthy" if result else "unhealthy"}
