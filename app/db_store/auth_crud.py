def email_access_level(conn, email):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT access_type FROM accounts WHERE email = %s
            """,
            (email,),
        )
        access_level = cur.fetchone()
        return access_level[0] if access_level else None
