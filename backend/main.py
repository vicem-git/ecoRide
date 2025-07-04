from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
db = SQLAlchemy(app)
