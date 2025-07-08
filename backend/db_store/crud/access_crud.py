# access CURD operations for user management


def get_user_by_email(conn, email):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM accounts WHERE email = %s", (email,))
        return cur.fetchone()  # returns None if not found


def create_account(conn, email, username, hashed_password):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO accounts (email, username, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (email, username, hashed_password),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
