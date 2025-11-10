import logging

logger = logging.getLogger(__name__)


def safe_close(app):
    try:
        if hasattr(app, "db_manager"):
            app.db_manager.close_all()
    except Exception as e:
        logger.error(f"Failed to close database pool on exit: {str(e)}")
