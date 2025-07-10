from flask import Flask
from app.db_manager import DatabaseManager
from app.routes import api_bp, html_bp
from config import db_config


def create_app():
    app = Flask(
        __name__,
        static_folder="app/static",
    )

    db_manager = DatabaseManager(db_config)
    app.db_manager = db_manager

    app.register_blueprint(api_bp)
    app.register_blueprint(html_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
