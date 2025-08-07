from flask import current_app
import json
from datetime import date, timedelta


def get_total_profits(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT balance FROM platform_balance 
        """)
        return cur.fetchone()


def get_trips_per_day(conn, period_start, period_end):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DATE(completed_at) AS trip_date, COUNT(*) as trip_count
            FROM trips
            WHERE status = (
                SELECT id FROM trip_status WHERE name = 'completed'
            )
            AND completed_at BETWEEN %s AND %s
            GROUP BY trip_date
            ORDER BY trip_date
        """,
            (period_start, period_end),
        )
        rows = {row[0]: row[1] for row in cur.fetchall()}

        # missing days filler
        current_date = period_start.date()
        last_date = period_end.date()
        results = []
        while current_date <= last_date:
            results.append(
                {
                    "date": current_date.isoformat(),
                    "total_trips": rows.get(current_date, 0),
                }
            )
            current_date += timedelta(days=1)


def get_profits_per_day(conn, period_start, period_end):
    platform_fee = 2
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 
                DATE(completed_at) AS day,
                COUNT(*) * %s AS total_earned
            FROM transactions
            WHERE status = (
                SELECT id FROM tx_status WHERE name = 'completed'
            )
            AND completed_at BETWEEN %s AND %s
            GROUP BY day
            ORDER BY day
        """,
            (platform_fee, period_start, period_end),
        )

        rows = {row[0]: row[1] for row in cur.fetchall()}

        # missing days filler
        current_date = period_start.date()
        last_date = period_end.date()
        results = []
        while current_date <= last_date:
            results.append(
                {
                    "date": current_date.isoformat(),
                    "total_earned": rows.get(current_date, 0),
                }
            )
            current_date += timedelta(days=1)


def get_moderators(conn):
    pass


def create_moderator(conn, name, email, password):
    pass


def suspend_account_by_id(conn, account_id):
    pass
