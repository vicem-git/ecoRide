from flask import current_app
from psycopg.rows import dict_row
from datetime import datetime
import json
from geopy.distance import geodesic
import logging

logger = logging.getLogger(__name__)

villes = {
    "Paris": {"lat": 48.85341, "lng": 2.34880},
    "Marseille": {"lat": 43.29695, "lng": 5.38107},
    "Lyon": {"lat": 45.74846, "lng": 4.84671},
    "Toulouse": {"lat": 43.60426, "lng": 1.44367},
    "Nice": {"lat": 43.70313, "lng": 7.26608},
    "Nantes": {"lat": 47.21725, "lng": -1.55336},
    "Strasbourg": {"lat": 48.58392, "lng": 7.74553},
    "Montpellier": {"lat": 43.61092, "lng": 3.87723},
    "Bordeaux": {"lat": 44.84044, "lng": -0.58050},
    "Lille": {"lat": 50.63297, "lng": 3.05858},
    "Rennes": {"lat": 48.11198, "lng": -1.67429},
    "Reims": {"lat": 49.25000, "lng": 4.03333},
    "Le Havre": {"lat": 49.49380, "lng": 0.10767},
    "Grenoble": {"lat": 45.17155, "lng": 5.72239},
    "Dijon": {"lat": 47.31667, "lng": 5.01667},
}


def reverse_lookup_coords(lat, lng):
    for city, coords in villes.items():
        if abs(coords["lat"] - lat) < 0.05 and abs(coords["lng"] - lng) < 0.05:
            return city
    return "Unknown"


def city_to_coords(city):
    if city in villes:
        coords = villes[city]
        if not coords:
            raise ValueError(f"City '{city}' not found in predefined cities.")

        point_wkt = f"POINT({coords['lng']} {coords['lat']})"
        return point_wkt


def add_user_to_trip(conn, trip_id, user_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO trip_passengers (trip_id, user_id)
            VALUES (%s, %s)
            ON CONFLICT (trip_id, user_id) DO NOTHING
            """,
            (trip_id, user_id),
        )
        added_psg = cur.rowcount > 0
        return True if added_psg else False


def remove_user_from_trip(conn, trip_id, user_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM trip_passengers WHERE trip_id = %s AND user_id = %s
        """,
            (trip_id, user_id),
        )
        return cur.rowcount > 0


def update_trip_status(conn, trip_id, new_status):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE trips SET status = %s
            WHERE id = %s
        """,
            (new_status, trip_id),
        )
        return cur.rowcount > 0


def create_trip(conn, driver_id, vehicle_id, start_city, end_city, start_time, price):
    start_point = city_to_coords(start_city)
    end_point = city_to_coords(end_city)
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO trips 
            (driver_id, vehicle_id,
            start_location, 
            end_location, start_time, 
            price, (SELECT id FROM trip_status WHERE name = 'upcoming'))
            VALUES (%s, %s, ST_GeomFromText(%s, 4326), ST_GeomFromText(%s, 4326), %s, %s, %s)
            RETURNING id""",
            (driver_id, vehicle_id, start_point, end_point, start_time, price),
        )
        trip_id = cur.fetchone()[0]
        return trip_id if trip_id else None


def cancel_trip(conn, trip_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE SET status = 'cancelled' FROM trips WHERE id = %s
        """,
            (trip_id,),
        )
        return cur.rowcount > 0


def get_trip_by_id(conn, trip_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM trips WHERE id = %s", (trip_id,))
        trip_data = cur.fetchone()
        return trip_data if trip_data else None


def get_trip_driver_id(conn, trip_id):
    with conn.cursor() as cur:
        cur.execute("SELECT driver_id FROM trips WHERE id = %s", (trip_id,))
        driver_id = cur.fetchone()
        return driver_id[0] if driver_id else None


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


def get_trip_passengers(conn, trip_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT user_id FROM trip_passengers
            WHERE trip_id = %s
        """,
            (trip_id,),
        )
        result = cur.fetchall()
        return [row["user_id"] for row in result] if result else []


def get_trip_passengers_userdata(conn, trip_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT user_id, username, email
            FROM trip_passengers_userdata
            WHERE trip_id = %s
            """,
            (trip_id,),
        )
        return cur.fetchall() or []


def get_passenger_trips(conn, user_id, status=None):
    with conn.cursor(row_factory=dict_row) as cur:
        query = """
            SELECT *
            FROM trip_with_status_and_summary t
            JOIN trip_passengers tp ON t.trip_id = tp.trip_id
            WHERE tp.user_id = %s
        """
        params = [user_id]
        if status is not None:
            query += " AND t.status = %s"
            params.append(status)
        query += " ORDER BY (t.summary->>'start_time')::timestamp DESC"
        cur.execute(query, params)
        trips = cur.fetchall()
        return trips if trips else []


def get_driver_trips(conn, driver_id, status=None):
    with conn.cursor(row_factory=dict_row) as cur:
        query = """
            SELECT *
            FROM trip_with_status_and_summary t
            WHERE driver_id = %s
        """
        params = [driver_id]
        if status is not None:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY (t.summary->>'start_time')::timestamp DESC"
        cur.execute(query, params)
        trips = cur.fetchall()
        return trips if trips else []


def set_trip_rating(conn, trip_id, rating):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE trips SET rating = %s WHERE id = %s",
            (rating, trip_id),
        )
        return True


def search_summaries_asst(
    conn,
    start_city=None,
    end_city=None,
    passenger_nr=None,
    start_date=None,
    max_price=None,
    energy_type=None,
    driver_rating=None,
):
    query = """
        SELECT *
        FROM trip_summaries_asst
        WHERE status IN ('pending', 'upcoming')
    """
    params = []

    if start_city:
        query += " AND summary->>'start_city' = %s"
        params.append(start_city.strip())

    if end_city:
        query += " AND summary->>'end_city' = %s"
        params.append(end_city.strip())

    if passenger_nr:
        query += " AND available_seats >= %s"
        params.append(int(passenger_nr))

    if start_date and start_date.lower() != "none":
        query += " AND (summary->>'start_time')::timestamp >= %s"
        params.append(start_date)

    if max_price:
        query += " AND (summary->>'price')::int <= %s"
        params.append(max_price)

    if energy_type:
        query += " AND summary -> 'vehicle' ->>'energy' = %s"
        params.append(energy_type)

    if driver_rating:
        query += " AND (summary->>'driver_rating')::float >= %s"
        params.append(int(driver_rating))

    query += " ORDER BY (summary->>'start_time')::timestamp ASC"

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        trips = cur.fetchall()

    return trips


def get_trip_summary_asst(conn, trip_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT *
            FROM trip_summaries_asst t
            WHERE t.trip_id = %s
            """,
            (trip_id,),
        )
        trip_summary = cur.fetchone()
        return trip_summary if trip_summary else None


def generate_trip_summary(conn, trip_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                t.id,
                ST_Y(t.start_location::geometry),
                ST_X(t.start_location::geometry),
                ST_Y(t.end_location::geometry),
                ST_X(t.end_location::geometry),
                t.start_time,
                t.price,
                d.rating,
                v.plate_number,
                v.model,
                v.color,
                b.name AS brand,
                e.name AS energy,
                u.username AS driver_name,
                u.photo_url as driver_photo
            FROM trips t
            JOIN driver_data d ON t.driver_id = d.id
            JOIN users u ON d.user_id = u.id
            JOIN vehicles v ON t.vehicle_id = v.id
            JOIN vehicle_brand b ON v.brand = b.id
            JOIN energy_types e ON v.energy_type = e.id
            WHERE t.id = %s
        """,
            (trip_id,),
        )

        row = cur.fetchone()
        if not row:
            raise ValueError(f"No trip found with ID: {trip_id}")

        (
            trip_id,
            start_lat,
            start_lng,
            end_lat,
            end_lng,
            start_time,
            price,
            rating,
            plate,
            model,
            color,
            brand,
            energy,
            driver_name,
            driver_photo,
        ) = row

        distance_km = geodesic((start_lat, start_lng), (end_lat, end_lng)).kilometers
        speed = 60 + (hash(trip_id) % 30)
        duration_min = round((distance_km / speed) * 60)

        start_city = reverse_lookup_coords(start_lat, start_lng)
        end_city = reverse_lookup_coords(end_lat, end_lng)

        summary = {
            "start_city": start_city,
            "end_city": end_city,
            "start_time": start_time.isoformat(),
            "distance_km": round(distance_km, 2),
            "estimated_duration_min": duration_min,
            "price": price,
            "vehicle": {
                "brand": brand,
                "model": model,
                "energy": energy,
                "color": color,
                "plate": plate,
            },
            "driver_name": driver_name,
            "driver_photo": driver_photo,
            "driver_rating": rating,
        }

        cur.execute(
            """
            INSERT INTO trip_summaries (trip_id, summary) 
            VALUES (%s, %s)
            ON CONFLICT (trip_id)
            DO UPDATE SET summary = EXCLUDED.summary
            RETURNING trip_id
        """,
            (trip_id, json.dumps(summary)),
        )

        summary_id = cur.fetchone()[0]
        return summary_id if summary_id else None


def regenerate_all_missing_summaries(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT t.id
            FROM trips t
            LEFT JOIN trip_summaries s ON s.trip_id = t.id
            WHERE s.trip_id IS NULL
        """)
        trip_ids = [row[0] for row in cur.fetchall()]

    counter = 0
    for trip_id in trip_ids:
        generate_trip_summary(conn, trip_id)
        counter += 1

    return counter
