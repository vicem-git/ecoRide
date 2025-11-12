from babel.dates import format_datetime
from datetime import datetime

def create_datetime_filter(app_locale):
    """
    Returns a Jinja2 filter function that formats datetime or ISO datetime strings
    according to the given locale.
    """
    def datetime_filter(value, format='short'):
        if not value:
            return ""  # handle None or empty strings gracefully

        # If it's a string, try to parse ISO 8601 datetime
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                # If parsing fails, just return the original string
                return value

        # Only format if it's a datetime object
        if isinstance(value, datetime):
            return format_datetime(value, format=format, locale=app_locale)

        # Otherwise, leave unchanged
        return value

    return datetime_filter
