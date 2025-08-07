from flask import current_app
import logging

# MODULE LOGGER
logger = logging.getLogger(__name__)


def allow_tx(conn, user_id, trip_id):
    print(f"Checking if {user_id} balance is sufficient for {trip_id} price")
    with conn.cursor() as cur:
        cur.execute("SELECT credits FROM users WHERE id = %s", (user_id,))
        user_balance = cur.fetchone()[0]

        cur.execute("SELECT price FROM trips WHERE id = %s", (trip_id,))
        trip_price = cur.fetchone()[0]

    allow_ok = user_balance >= trip_price
    return {
        "allow_ok": allow_ok,
        "trip_price": trip_price,
        "user_balance": user_balance,
    }


def create_tx(conn, tx_from, tx_to, amount, trip_id):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET credits = credits - %s WHERE id = %s",
            (amount, tx_from),
        )

        cur.execute(
            """
            INSERT INTO transactions (tx_from, tx_to, amount, trip_id, status)
            VALUES (%s, %s, %s, %s, (SELECT id from tx_status WHERE name = 'pending'))
            RETURNING id
            """,
            (tx_from, tx_to, amount, trip_id),
        )
        tx_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO trip_txs (trip_id, tx_id)
            VALUES (%s, %s)
        """,
            (
                trip_id,
                tx_id,
            ),
        )
    return tx_id if tx_id else None


def complete_tx(conn, trip_id):
    platform_fee = 2
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE transactions
            SET status = (SELECT id FROM tx_status WHERE name = 'completed')
            WHERE id = %s
            RETURNING id, amount
        """,
            (trip_id,),
        )
        tx_id = cur.fetchone()[0]
        tx_amount = cur.fetchone()[1]

        cur.execute(
            """
            UPDATE users
            SET credits = credits + %s - %s
            WHERE id = (SELECT tx_to FROM transactions WHERE tx_id = %s)
        """,
            (tx_amount, platform_fee, tx_id),
        )

        cur.execute(
            "UPDATE platform_balance SET balance = balance + %s", (platform_fee,)
        )

        return tx_id if tx_id else None


def update_tx_status(conn, tx_id, status):
    pass


def get_tx_by_id(conn, tx_id):
    pass


def get_trip_txs(conn, trip_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM trip_txs
            WHERE trip_id = %s
        """,
            (trip_id,),
        )
        result = cur.fetchall()
        trip_txs = [tx[0] for tx in result]
        return trip_txs
