from flask import current_app
from psycopg.rows import dict_row
import json
from datetime import date, timedelta


def get_platform_balance(conn):
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
                    "trip_date": current_date.isoformat(),
                    "total_trips": rows.get(current_date, 0),
                }
            )
            current_date += timedelta(days=1)
        return results


def get_income_per_day(conn, period_start, period_end):
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
                    "income_date": current_date.isoformat(),
                    "total_earned": rows.get(current_date, 0),
                }
            )
            current_date += timedelta(days=1)
        return results


def get_moderators(conn):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, email, status
            FROM accounts
            WHERE access_type = (
                SELECT id FROM account_access_type WHERE name = 'moderator'
            )
            ORDER BY created_at DESC
        """
        )
        return cur.fetchall()


def create_moderator(conn, email, password):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO accounts (email, password_hash, access_type, status)
            VALUES (%s, %s, (SELECT id FROM account_access_type WHERE name = 'moderator'), (SELECT id FROM account_status WHERE name = 'active'))
            RETURNING id
        """,
            (email, password),
        )
        return cur.fetchone()[0]


def suspend_account_by_id(conn, account_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE accounts a 
            SET status = (SELECT id FROM account_status WHERE name = 'suspended')
            WHERE a.id = %s
        """,
            (account_id,),
        )
        return cur.rowcount > 0


def activate_account_by_id(conn, account_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE accounts a 
            SET status = (SELECT id FROM account_status WHERE name = 'active')
            WHERE a.id = %s
        """,
            (account_id,),
        )
        return cur.rowcount > 0


def query_users(conn, search_term, limit=10):
    search_pattern = f"%{search_term.strip()}%" if search_term else "%"
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT a.id AS account_id, a.email, u.username, s.name AS status
            FROM users u
            JOIN accounts a ON u.account_id = a.id
            JOIN account_status s ON a.status = s.id
            WHERE a.email ILIKE %s
               OR u.username ILIKE %s
               OR s.name ILIKE %s
            ORDER BY a.email
            LIMIT %s
            """,
            (search_pattern, search_pattern, search_pattern, limit),
        )
        return cur.fetchall()
