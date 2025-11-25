from flask import current_app
from psycopg.rows import dict_row

def get_pending_reviews(batch, filter):
    pending = current_app.mongo_store.get_reviews_by_status(moderated=False, batch=batch, filter=filter)
    return pending

def get_trip_details(conn, trip_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT t.id AS trip_id, t.driver_id AS driver_id, ts.summary AS summary
            FROM trips t
            JOIN trip_summaries ts ON t.id = ts.trip_id 
            WHERE t.id = %s
            """,
            (trip_id,),
        )
        trip_details = cur.fetchone()
        return trip_details if trip_details else None
