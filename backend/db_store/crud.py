def test_connection(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            return result[0] == 1
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
