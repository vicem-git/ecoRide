from flask import Flask
from app.db_store import DatabaseManager
from app.routes import api_bp, html_bp
from config import db_config, Config
from app.utils import bcrypt, login_manager
from app.models import load_user


def create_app():
    app = Flask(
        __name__,
        static_folder="app/static",
    )

    app.config.from_object(Config)

    bcrypt.init_app(app)

    db_manager = DatabaseManager(db_config)
    app.db_manager = db_manager
    app.pool = db_manager.pool

    login_manager.init_app(app)
    load_user(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(html_bp)

    @app.teardown_appcontext
    def cleanup(exc):
        if hasattr(app, "pool"):
            try:
                app.pool.close()
            except Exception as e:
                app.logger.error(f"Failed to close database pool: {str(e)}")

    # SAFE CLOSING ON EXIT
    import atexit

    def safe_close():
        try:
            if hasattr(app, "pool"):
                app.pool.close()
        except Exception as e:
            print(f"Failed to close database pool on exit: {str(e)}")

    atexit.register(safe_close)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
