from flask_sqlalchemy import SQLAlchemy

alchemy_db = SQLAlchemy()
Base = alchemy_db.Model
