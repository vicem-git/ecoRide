# filters.py
from babel.dates import format_datetime
from datetime import datetime

def create_datetime_filter(app_locale):
    """
    Returns a Jinja2 filter function that formats datetime objects
    according to the given locale.
    """
    def datetime_filter(value, format='short'):
        if not isinstance(value, datetime):
            return value  # leave non-datetime objects unchanged
        return format_datetime(value, format=format, locale=app_locale)
    
    return datetime_filter