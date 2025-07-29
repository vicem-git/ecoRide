from psycopg.rows import dict_row


def create_tripp(conn, trip_data):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO trips 
            (driver_id, vehicle_id,
            start_location, 
            end_location, start_time, 
            price, trip_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id""",
            (
                trip_data["driver_id"],
                trip_data["start_location"],
                trip_data["end_location"],
                trip_data["start_time"],
                trip_data["end_time"],
                trip_data["price"],
                trip_data["trip_status"],
            ),
        )
        trip_id = cur.fetchone()[0]
        conn.commit()
        return trip_id


def get_trip_by_id(conn, trip_id):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM trips WHERE id = %s", (trip_id,))
        trip_data = cur.fetchone()
        return trip_data if trip_data else None


def update_trip_status(conn, trip_id, new_status):
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("UPDATE trips SET status = %s WHERE id = %s", (new_status, trip_id))
        conn.commit()
        return True


def get_trip_available_seats(conn, trip_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT available_seats
            FROM trip_available_seats
            WHERE trip_id = %s
            """,
            (trip_id,),
        )
        result = cur.fetchone()
        available_seats = result[0] if result else None
        return available_seats


def get_user_trips(conn, user_id, status):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT t.*
            FROM trips t
            JOIN trip_passengers tp ON t.id = tp.trip_id
            WHERE tp.user_id = %s AND t.trip_status = %s
        """,
            (user_id, status),
        )
        trips = cur.fetchall()
        return trips if trips else None


def set_trip_rating(conn, trip_id, rating):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE trips SET rating = %s WHERE id = %s",
            (rating, trip_id),
        )
        conn.commit()
        return True


def search_trips(
    conn,
    start_city=None,
    end_city=None,
    passenger_nr=None,
    max_price=None,
    start_date=None,
):
    query = """
        SELECT s.*
        FROM trip_summaries s
        WHERE 1=1
    """
    params = []

    if start_city:
        query += " AND s.summary->>'start_city' = %s"
        params.append(start_city)

    if end_city:
        query += " AND s.summary->>'end_city' = %s"
        params.append(end_city)

    if max_price:
        query += " AND (s.summary->>'price')::int <= %s"
        params.append(max_price)

    if start_date and start_date.lower() != "none":
        query += " AND (s.summary->>'start_time')::timestamp >= %s"
        params.append(start_date)

    query += " ORDER BY (s.summary->>'start_time')::timestamp ASC"

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        trips = cur.fetchall()

    for trip in trips:
        trip_id = trip.get("trip_id")
        trip["available_seats"] = get_trip_available_seats(conn, trip_id)

    if passenger_nr:
        passenger_nr = int(passenger_nr)
        trips = [trip for trip in trips if trip["available_seats"] >= int(passenger_nr)]

    return trips if trips else None
