from flask import Flask
import logging
from app.db_store import DatabaseManager, crud_utilities
from app.routes import api_bp, html_bp
from config import db_config, Config
from app.utils import bcrypt, login_manager, safe_close
from app.models import session_user_loader
import atexit


def create_app():
    app = Flask(
        __name__,
        static_folder="app/static",
    )

    logging.basicConfig(level=logging.INFO)
    app.config.from_object(Config)
    bcrypt.init_app(app)
    db_manager = DatabaseManager(db_config)
    app.db_manager = db_manager

    try:
        app.static_ids = crud_utilities.load_static_ids(db_manager)
        logging.info("static ids loaded ~")
    except Exception as e:
        logging.error(f"failed to load static ids: {str(e)}")

    login_manager.init_app(app)
    session_user_loader(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(html_bp)

    login_manager.login_view = "html.login"

    # SAFE CLOSING ON EXIT
    atexit.register(safe_close, app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
