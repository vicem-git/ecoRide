from psycopg.rows import dict_row


def get_pending_reviews(conn):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT r.id, r.trip_id, u.username, r.rating, r.comments 
            FROM reviews r
            JOIN users u ON r.author_id = u.id
            WHERE review_status_id = (SELECT id FROM review_status WHERE name = 'pending')
            AND rating >= 3
            """
        )
        reviews = cur.fetchall()
        return reviews if reviews else []


def get_pending_negative(conn):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, trip_id, author_id, rating, comments 
            FROM reviews 
            WHERE review_status_id = (SELECT id FROM review_status WHERE name = 'pending')
            AND rating < 3
            """
        )
        reviews = cur.fetchall()
        return reviews if reviews else []


def get_review_by_id(conn, review_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, trip_id, author_id, rating, comments, status 
            FROM reviews 
            WHERE id = %s
            """,
            (review_id,),
        )
        review = cur.fetchone()
        return review if review else None


def get_trip_details(conn, trip_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT driver_id, start_location, end_location, start_time, completed_at,
            FROM trips
            WHERE id = %s
            """,
            (trip_id,),
        )
        trip_details = cur.fetchone()
        return trip_details if trip_details else None
