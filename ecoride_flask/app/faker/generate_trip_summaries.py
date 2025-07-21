import psycopg
from app.faker.villes import villes
from geopy.distance import geodesic
import random
import logging
import json
import os

# MODULE LOGGER
logger = logging.getLogger(__name__)


db_user = "ecoride_admin"
db_password = "mar-courbet-game-pollo"
db_host = "localhost"
db_port = 5432
db_name = "ecoride_db"
conninfo = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def reverse_lookup_coords(lat, lng):
    for city, coords in villes.items():
        if abs(coords["lat"] - lat) < 0.05 and abs(coords["lng"] - lng) < 0.05:
            return city
    return "Unknown"


def generate_summaries(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                t.id,
                ST_Y(t.start_location::geometry),
                ST_X(t.start_location::geometry),
                ST_Y(t.end_location::geometry),
                ST_X(t.end_location::geometry),
                t.price,
                d.rating,
                v.plate_number,
                v.model,
                v.color,
                v.number_of_seats,
                b.name AS brand,
                e.name AS energy
            FROM trips t
            JOIN driver_data d ON t.driver_id = d.id
            JOIN vehicles v ON t.vehicle_id = v.id
            JOIN vehicle_brand b ON v.brand = b.id
            JOIN energy_types e ON v.energy_type_id = e.id
            WHERE NOT EXISTS (
                SELECT 1 FROM trip_summaries s WHERE s.trip_id = t.id
            )
        """)

        rows = cur.fetchall()

        for row in rows:
            (
                trip_id,
                start_lat,
                start_lng,
                end_lat,
                end_lng,
                price,
                rating,
                plate,
                model,
                color,
                seats,
                brand,
                energy,
            ) = row

            distance_km = geodesic(
                (start_lat, start_lng), (end_lat, end_lng)
            ).kilometers
            speed = 60 + (hash(trip_id) % 30)  # semi-random but deterministic
            duration_min = round((distance_km / speed) * 60)

            start_city = reverse_lookup_coords(start_lat, start_lng)
            end_city = reverse_lookup_coords(end_lat, end_lng)

            cur.execute(
                "SELECT COUNT(*) FROM trip_passengers WHERE trip_id = %s", (trip_id,)
            )
            passenger_count = cur.fetchone()[0]

            summary = {
                "start_city": start_city,
                "end_city": end_city,
                "distance_km": round(distance_km, 2),
                "estimated_duration_min": duration_min,
                "price": price,
                "vehicle": {
                    "brand": brand,
                    "model": model,
                    "energy": energy,
                    "seats": seats,
                    "color": color,
                    "plate": plate,
                },
                "passenger_count": passenger_count,
                "driver_rating": rating,
            }

            cur.execute(
                "INSERT INTO trip_summaries (trip_id, summary) VALUES (%s, %s)",
                (trip_id, json.dumps(summary)),
            )

        conn.commit()
        print(f"✅ {len(rows)} trip summaries generated.")


if __name__ == "__main__":
    with psycopg.connect(conninfo=conninfo) as conn:
        generate_summaries(conn)
        conn.close()
