from flask import current_app


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
            cur.execute(f"SET search_path TO {schema_name};")
            print(f"Search path set to : {schema_name}")
    except Exception as e:
        print(f"Failed to set search path: {e}")
        raise


def load_static_ids(conn):
    ids = {}

    with conn.cursor() as cur:
        # Load account_access
        cur.execute("SELECT name, id FROM account_access;")
        ids["account_access"] = dict(cur.fetchall())

        # Load account_status
        cur.execute("SELECT name, id FROM account_status;")
        ids["account_status"] = dict(cur.fetchall())

    return ids
