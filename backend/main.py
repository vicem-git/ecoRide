from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv("../.env")

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

db = SQLAlchemy(app)


@app.route("/")
def index():
    return app.send_static_file("index.html")
