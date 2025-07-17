from flask import current_app
from psycopg import sql
from psycopg.rows import dict_row


def test_connection(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            return result[0] == 1
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def configure_conn(conn, schema_name):
    try:
        with conn.cursor() as cur:
            query = sql.SQL("SET search_path TO {}").format(sql.Identifier(schema_name))
            cur.execute(query)
            print(f"Search path set to : {schema_name}")
    except Exception as e:
        print(f"Failed to set search path: {e}")
        raise


def load_static_ids(conn):
    ids = {}

    with conn.cursor(row_factory=dict_row) as cur:
        # Load account_access
        cur.execute("SELECT name, id FROM account_access;")
        rows = cur.fetchall()
        ids["account_access"] = {
            row["name"]: str(row["id"]) if not isinstance(row["id"], str) else row["id"]
            for row in rows
        }

        # Load account_status
        cur.execute("SELECT name, id FROM account_status;")
        rows = cur.fetchall()
        ids["account_status"] = {
            row["name"]: str(row["id"]) if not isinstance(row["id"], str) else row["id"]
            for row in rows
        }

    return ids
