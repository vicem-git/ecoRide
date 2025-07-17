from flask import Flask
from app.db_store import DatabaseManager, crud_utilities
from app.routes import api_bp, html_bp
from config import db_config, Config
from app.utils import bcrypt, login_manager
from app.models import session_user_loader


def create_app():
    app = Flask(
        __name__,
        static_folder="app/static",
    )

    app.config.from_object(Config)

    bcrypt.init_app(app)

    db_manager = DatabaseManager(db_config)
    app.db_manager = db_manager

    with app.db_manager.connection() as conn:
        app.static_ids = crud_utilities.load_static_ids(conn)

    print(app.static_ids)

    login_manager.init_app(app)
    session_user_loader(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(html_bp)

    login_manager.login_view = "html.login"

    # SAFE CLOSING ON EXIT
    import atexit

    def safe_close():
        try:
            if hasattr(app, "pool"):
                app.db_manager.close_all()
        except Exception as e:
            print(f"Failed to close database pool on exit: {str(e)}")

    atexit.register(safe_close)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
