from faker import Faker
import psycopg
from uuid import uuid4
import random
from datetime import datetime, timedelta

fake = Faker("fr_FR")


def get_id(cur, table, name):
    cur.execute(f"SELECT id FROM {table} WHERE name = %s", (name,))
    return cur.fetchone()[0]


def seed_data(conn, num_drivers=5, num_passengers=10, trips_per_driver=3):
    with conn.cursor() as cur:
        # Get static IDs
        access_id = get_id(cur, "account_access", "user")
        status_id = get_id(cur, "account_status", "active")
        driver_role_id = get_id(cur, "roles", "driver")
        passenger_role_id = get_id(cur, "roles", "passenger")
        trip_status_ids = [row[0] for row in cur.execute("SELECT id FROM trip_status")]

        # Create passengers
        passenger_ids = []
        for _ in range(num_passengers):
            account_id = str(uuid4())
            user_id = str(uuid4())
            cur.execute(
                "INSERT INTO accounts (id, email, password_hash, account_access_id, account_status_id) VALUES (%s, %s, %s, %s, %s)",
                (account_id, fake.email(), "fakehash", access_id, status_id),
            )
            cur.execute(
                "INSERT INTO users (id, account_id, username) VALUES (%s, %s, %s)",
                (user_id, account_id, fake.user_name()),
            )
            cur.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                (user_id, passenger_role_id),
            )
            passenger_ids.append(user_id)

        # Create drivers and trips
        for _ in range(num_drivers):
            account_id = str(uuid4())
            user_id = str(uuid4())
            cur.execute(
                "INSERT INTO accounts (id, email, password_hash, account_access_id, account_status_id) VALUES (%s, %s, %s, %s, %s)",
                (account_id, fake.email(), "fakehash", access_id, status_id),
            )
            cur.execute(
                "INSERT INTO users (id, account_id, username) VALUES (%s, %s, %s)",
                (user_id, account_id, fake.user_name()),
            )
            cur.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                (user_id, driver_role_id),
            )

            driver_id = str(uuid4())
            cur.execute(
                "INSERT INTO driver_data (id, user_id, rating) VALUES (%s, %s, %s)",
                (driver_id, user_id, random.randint(3, 5)),
            )

            # Get random brand and energy
            cur.execute("SELECT id FROM vehicle_brand ORDER BY RANDOM() LIMIT 1")
            brand_id = cur.fetchone()[0]
            cur.execute("SELECT id FROM energy_types ORDER BY RANDOM() LIMIT 1")
            energy_id = cur.fetchone()[0]

            vehicle_id = str(uuid4())
            cur.execute(
                """
                INSERT INTO vehicles (
                    id, plate_number, registration_date, brand, model, color, number_of_seats, energy_type_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    vehicle_id,
                    fake.license_plate(),
                    fake.date_between(start_date="-3y", end_date="-1y"),
                    brand_id,
                    fake.word(),
                    fake.color_name(),
                    random.randint(2, 5),
                    energy_id,
                ),
            )

            # Insert trips for this driver
            for _ in range(trips_per_driver):
                trip_id = str(uuid4())
                start_lat, start_lng = fake.latitude(), fake.longitude()
                end_lat, end_lng = fake.latitude(), fake.longitude()
                start_time = fake.date_time_between(start_date="+1d", end_date="+30d")
                price = random.randint(500, 5000)
                trip_status = random.choice(trip_status_ids)

                cur.execute(
                    """
                    INSERT INTO trips (
                        id, driver_id, vehicle_id,
                        start_location, end_location,
                        start_time, price, trip_status
                    ) VALUES (
                        %s, %s, %s,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                        %s, %s, %s
                    )
                """,
                    (
                        trip_id,
                        user_id,
                        vehicle_id,
                        start_lng,
                        start_lat,
                        end_lng,
                        end_lat,
                        start_time,
                        price,
                        trip_status,
                    ),
                )

                # Add random passengers
                chosen_passengers = random.sample(passenger_ids, random.randint(1, 3))
                for pid in chosen_passengers:
                    cur.execute(
                        "INSERT INTO trip_passengers (trip_id, user_id) VALUES (%s, %s)",
                        (trip_id, pid),
                    )

                # Add reviews
                for pid in chosen_passengers:
                    review_id = str(uuid4())
                    rating = random.randint(3, 5)
                    comment = fake.sentence()
                    review_status_id = get_id(cur, "review_status", "approved")
                    cur.execute(
                        """
                        INSERT INTO reviews (
                            id, trip_id, author_id, rating, comments, review_status_id
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                        (review_id, trip_id, pid, rating, comment, review_status_id),
                    )

        conn.commit()

