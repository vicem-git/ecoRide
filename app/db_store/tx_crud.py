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
    pending_status = current_app.static_ids["tx_status"]["pending"]
    print(
        f"Creating transaction from {tx_from} to {tx_to} with amount {amount}, status {pending_status}"
    )
    # deduce @from
    # create transaction
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET credits = credits - %s WHERE id = %s",
            (amount, tx_from),
        )

        cur.execute(
            """
            INSERT INTO transactions (tx_from, tx_to, amount, trip_id, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (tx_from, tx_to, amount, trip_id, pending_status),
        )
        tx_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO trip_txs (trip_id, tx_id)
        """,
            (tx_id,),
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


def rollback_tx(conn, tx_id):
    logger.info(f"Rolling back transaction {tx_id}")
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE transactions
            SET status = %s
            WHERE id = %s
            RETURNING tx_from
            """,
            (current_app.static_ids["tx_status"]["failed"], tx_id),
        )
        tx_from = cur.fetchone()[0]

        # refund @from
        cur.execute(
            """
            UPDATE users SET credits = credits + (
                SELECT amount FROM transactions WHERE id = %s
            )
            WHERE id = (
                SELECT tx_from FROM transactions WHERE id = %s
            )
        """,
            (tx_from, tx_id),
        )
