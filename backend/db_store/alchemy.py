from flask_sqlalchemy import SQLAlchemy

alchemy_db = SQLAlchemy()
Base = alchemy_db.Model

# Base = declarative_base(metadata=alchemy_db.metadata) ??
