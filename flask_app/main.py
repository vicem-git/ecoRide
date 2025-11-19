from flask import Flask, session
from rich.logging import RichHandler
import logging
from app.db_store import DatabaseManager, MongoStore, crud_utilities, trips_crud
from app.routes import pages_bp
from app.routes.api import admin_bp, auth_bp, drivers_bp, mods_bp, trips_bp, users_bp
from config import db_config, mongo_config, Config
from app.utils import (
    bcrypt,
    login_manager,
    safe_close,
    create_datetime_filter,
    register_template_helpers,
    valid_csrf
)
from app.models import session_user_loader
import atexit
from datetime import datetime
from babel import Locale
from app.faker import seed_data, villes

APP_LOCALE = 'fr_FR'
locale_obj = Locale.parse(APP_LOCALE)

def create_app():
    app = Flask(
        __name__,
        static_folder="app/static",
    )

    app.jinja_env.filters["fr_date"] = create_datetime_filter(APP_LOCALE)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(markup=True)],
    )

    # MAYBE UNCOMMENT IN PROD
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    app.config.from_object(Config)
    bcrypt.init_app(app)
    db_manager = DatabaseManager(db_config)
    app.db_manager = db_manager
    
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("pymongo.monitoring").setLevel(logging.WARNING)   
    mongo_store = MongoStore(mongo_config)
    app.mongo_store = mongo_store

    logging.info(
        f"[bold green]TIME NOW : {datetime.now().strftime('%d %B %Y - %H:%Mhs')}[/bold green]"
    )

    try:
        app.static_ids = crud_utilities.load_static_ids(db_manager)
        logging.info("static ids loaded ~")
    except Exception as e:
        logging.error(f"failed to load static ids: {str(e)}")

    # STATIC IDS TEMPLATE HELPERS
    register_template_helpers(app)

    # DB SEEDING AND SUMMARY GENERATION
    try:
        with db_manager.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users")
                user_count = cur.fetchone()[0]
                conn.commit()
            if user_count < 10:
                seed_data(
                    conn,
                    num_drivers=500,
                    num_users=100,
                    completed_trips=3,
                    upcoming_trips=5,
                )
                logging.info("DB SEED : Database seeded.")
            else:
                logging.info("DB SEED : Seeding skipped: users already exist.")

        with db_manager.connection() as conn:
            try:
                count = trips_crud.regenerate_all_missing_summaries(conn)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

            if count:
                logging.info(f"BATCH SUMMARIES: {count} summaries generated.")
            else:
                logging.info(
                    "BATCH SUMMARIES: Summary generation skipped: data already present."
                )

    except Exception as e:
        logging.error(f"DB SEED ERROR: {e}")

    login_manager.init_app(app)
    session_user_loader(app)

    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(mods_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(users_bp)

    @app.context_processor
    def inject_year():
        return {"current_year": datetime.now().year}

    @app.context_processor
    def inject_cities():
        cities = list(villes.keys())
        return {"cities": cities}

    @app.context_processor
    def inject_static_ids():
        return dict(static_ids=app.static_ids)
    
    # CSRF 
    @app.before_request
    def ensure_csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
    
    @app.before_request
    def csrf_protect():
        view = app.view_functions.get(request.endpoint)
        if view and getattr(view, "_skip_csrf", False):
            return  # skip

        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            token = request.headers.get("X-CSRFToken")
            if not valid_csrf(token):
                abort(400, "Invalid CSRF token")

    login_manager.login_view = "pages.login"

    # SAFE CLOSING ON EXIT
    atexit.register(safe_close, app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
