from flask import current_app
from psycopg import sql
from faker import Faker
from uuid import uuid4
import random
from app.faker.villes import villes
import logging

# MODULE LOGGER
logger = logging.getLogger(__name__)

fake = Faker("fr_FR")

photo_urls = [
    "graphics/profiles/profile1.jpg",
    "graphics/profiles/profile2.jpg",
    "graphics/profiles/profile3.jpg",
    "graphics/profiles/profile4.jpg",
    "graphics/profiles/profile5.jpg",
    "graphics/profiles/profile6.jpg",
    "graphics/profiles/profile7.jpg",
    "graphics/profiles/profile8.jpg",
    "graphics/profiles/profile9.jpg",
    "graphics/profiles/profile10.jpg",
    "graphics/profiles/profile11.jpg",
    "graphics/profiles/profile12.jpg",
    "graphics/profiles/profile13.jpg",
    "graphics/profiles/profile14.jpg",
    "graphics/profiles/profile15.jpg",
    "graphics/profiles/profile16.jpg",
    "graphics/profiles/profile17.jpg",
    "graphics/profiles/profile18.jpg",
    "graphics/profiles/profile19.jpg",
    "graphics/profiles/profile20.jpg",
    "graphics/profiles/profile21.jpg",
    "graphics/profiles/profile22.jpg",
    "graphics/profiles/profile23.jpg",
    "graphics/profiles/profile24.jpg",
    "graphics/profiles/profile25.jpg",
    "graphics/profiles/profile26.jpg",
    "graphics/profiles/profile27.jpg",
    "graphics/profiles/profile28.jpg",
    "graphics/profiles/profile29.jpg",
]


car_models = [
    ("citadine", 4),  # city car
    ("berline", 5),  # sedan
    ("coupé", 2),
    ("break", 5),  # station wagon
    ("minivan", 7),  # minivan
    ("SUV", 5),
    ("cabriolé", 2),  # convertible
    ("fourgon", 3),  # van
]


def random_ville():
    city = random.choice(list(villes.keys()))
    coords = villes[city]
    return {
        "label": city,
        "lat": coords["lat"],
        "lng": coords["lng"],
    }


def is_value_unique(cur, table, column, value):
    query = sql.SQL("SELECT 1 FROM {table} WHERE {column} = %s LIMIT 1").format(
        table=sql.Identifier(table),
        column=sql.Identifier(column),
    )
    cur.execute(query, (value,))
    return cur.fetchone() is None


def get_unique_email(cur, max_attempts=20):
    for _ in range(max_attempts):
        email = fake.email()
        if is_value_unique(cur, "accounts", "email", email):
            return email
    raise ValueError("Unable to generate unique email")


def get_unique_username(cur, max_attempts=20):
    for _ in range(max_attempts):
        username = fake.user_name()
        if is_value_unique(cur, "users", "username", username):
            return username
    raise ValueError("Unable to generate unique username")


def random_photo_url():
    photo = random.choice(photo_urls)
    return photo


def get_unique_license_plate(cur, max_attempts=20):
    for _ in range(max_attempts):
        plate = fake.license_plate()
        if is_value_unique(cur, "vehicles", "plate_number", plate):
            return plate
    raise ValueError("Unable to generate unique license plate")


def get_id(cur, table, name):
    query = sql.SQL("SELECT id FROM {table} WHERE name = %s").format(
        table=sql.Identifier(table)
    )
    cur.execute(query, (name,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"No ID found for name '{name}' in table '{table}'")
    return row[0]


def seed_data(conn, num_drivers, num_users, completed_trips, upcoming_trips):
    try:
        with conn.cursor() as cur:
            # Get static IDs
            access_id = get_id(cur, "account_access_type", "user")
            status_id = get_id(cur, "account_status", "active")
            driver_role_id = get_id(cur, "roles", "driver")
            passenger_role_id = get_id(cur, "roles", "passenger")

            # Create users
            passenger_ids = []
            for _ in range(num_users):
                email = get_unique_email(cur)
                username = get_unique_username(cur)
                account_id = str(uuid4())
                user_id = str(uuid4())
                photo = random_photo_url()
                cur.execute(
                    "INSERT INTO accounts (id, email, password_hash, access_type, status) VALUES (%s, %s, %s, %s, %s)",
                    (account_id, email, "fakehash", access_id, status_id),
                )
                cur.execute(
                    "INSERT INTO users (id, account_id, username, photo_url) VALUES (%s, %s, %s, %s)",
                    (user_id, account_id, username, photo),
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
                email = get_unique_email(cur)
                username = get_unique_username(cur)
                photo = random_photo_url()
                cur.execute(
                    "INSERT INTO accounts (id, email, password_hash, access_type, status) VALUES (%s, %s, %s, %s, %s)",
                    (account_id, email, "fakehash", access_id, status_id),
                )
                cur.execute(
                    "INSERT INTO users (id, account_id, username, photo_url) VALUES (%s, %s, %s, %s)",
                    (user_id, account_id, username, photo),
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
                license_plate = get_unique_license_plate(cur)
                vehicle_id = str(uuid4())
                model, max_seats = random.choice(car_models)
                cur.execute(
                    """
                    INSERT INTO vehicles (
                        id, driver_id, plate_number, registration_date, brand, model, color, number_of_seats, energy_type
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        vehicle_id,
                        driver_id,
                        license_plate,
                        fake.date_between(start_date="-3y", end_date="-1y"),
                        brand_id,
                        model,
                        fake.color_name(),
                        max_seats,
                        energy_id,
                    ),
                )

                # Insert UPCOMING trips for this driver
                for _ in range(upcoming_trips):
                    start = random_ville()
                    end = random_ville()
                    trip_id = str(uuid4())
                    start_lat, start_lng = start["lat"], start["lng"]
                    end_lat, end_lng = end["lat"], end["lng"]
                    start_time = fake.date_time_between(
                        start_date="+1d", end_date="+30d"
                    )
                    price = random.randint(5, 15)

                    cur.execute(
                        """
                        INSERT INTO trips (
                            id, driver_id, vehicle_id,
                            start_location, end_location,
                            start_time, price, status
                        ) VALUES (
                            %s, %s, %s,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            %s, %s, (SELECT id FROM trip_status WHERE name = 'upcoming')
                        )""",
                        (
                            trip_id,
                            driver_id,
                            vehicle_id,
                            start_lng,
                            start_lat,
                            end_lng,
                            end_lat,
                            start_time,
                            price,
                        ),
                    )

                    cur.execute(
                        "SELECT number_of_seats FROM vehicles WHERE id = %s",
                        (vehicle_id,),
                    )
                    max_passengers = cur.fetchone()[0]

                    num_passengers = random.randint(1, min(3, max_passengers))
                    chosen_passengers = random.sample(passenger_ids, num_passengers)

                    for pid in chosen_passengers:
                        cur.execute(
                            "INSERT INTO trip_passengers (trip_id, user_id) VALUES (%s, %s)",
                            (trip_id, pid),
                        )

                # Insert PAST trips for this driver
                for _ in range(completed_trips):
                    start = random_ville()
                    end = random_ville()
                    trip_id = str(uuid4())
                    start_lat, start_lng = start["lat"], start["lng"]
                    end_lat, end_lng = end["lat"], end["lng"]
                    start_time = fake.date_time_between(
                        start_date="-30d", end_date="-1d"
                    )
                    price = random.randint(5, 15)
                    completed_at = start_time

                    cur.execute(
                        """
                        INSERT INTO trips (
                            id, driver_id, vehicle_id,
                            start_location, end_location,
                            start_time, price, status, completed_at
                        ) VALUES (
                            %s, %s, %s,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            %s, %s, (SELECT id FROM trip_status WHERE name ='completed'), %s
                        ) RETURNING id""",
                        (
                            trip_id,
                            driver_id,
                            vehicle_id,
                            start_lng,
                            start_lat,
                            end_lng,
                            end_lat,
                            start_time,
                            price,
                            completed_at,
                        ),
                    )

                    trip_id = cur.fetchone()[0]

                    cur.execute(
                        "SELECT number_of_seats FROM vehicles WHERE id = %s",
                        (vehicle_id,),
                    )
                    max_passengers = cur.fetchone()[0]

                    num_passengers = random.randint(1, min(3, max_passengers))
                    chosen_passengers = random.sample(passenger_ids, num_passengers)

                    for pid in chosen_passengers:
                        cur.execute(
                            "INSERT INTO trip_passengers (trip_id, user_id) VALUES (%s, %s)",
                            (trip_id, pid),
                        )

                    # create TX
                    for pid in chosen_passengers:
                        tx_from = pid
                        tx_to = user_id
                        amount = price
                        trip_id = trip_id
                        completed_at = completed_at

                        cur.execute(
                            """
                            INSERT INTO transactions (
                                tx_from, tx_to, amount, trip_id, completed_at, status
                            ) VALUES (%s, %s, %s, %s, %s, (SELECT id FROM tx_status WHERE name = 'completed'))
                            """,
                            (tx_from, tx_to, amount, trip_id, completed_at),
                        )

                        cur.execute(
                            "UPDATE platform_balance SET balance = balance + 2 "
                        )

                    # Add PENDING reviews for moderation TEST
                    # RATE TRIP
                    for pid in chosen_passengers: 
                        comment = fake.sentence()
                        status = "pending"
                        evaluation = random.choice(["positive", "negative"])
                        moderated = random.choice([False, True])
                        if evaluation == "positive":
                            driver_rating = random.randint(3, 5)
                        elif evaluation == "negative":
                            driver_rating = random.randint(1,2)
                        review_ok = current_app.mongo_store.add_trip_review(
                                trip_id=trip_id,
                                driver_id=driver_id,
                                passenger_id=pid,
                                trip_evaluation=evaluation,
                                driver_rating=driver_rating,
                                review_comment=comment,
                                moderated=moderated
                        )
                        if not review_ok:
                            raise Exception("REVIEW ERROR")
 
        conn.commit()
    except Exception as e:
        logger.error(f"DB SEED ERROR : {e}")
        raise


def seed_trips_only(conn, completed_trips, upcoming_trips):
    """Generate trips for existing drivers/passengers. Does NOT commit — caller is responsible."""
    try:
        with conn.cursor() as cur:
            # Fetch existing passengers
            cur.execute(
                "SELECT u.id FROM users u "
                "JOIN user_roles ur ON ur.user_id = u.id "
                "JOIN roles r ON r.id = ur.role_id "
                "WHERE r.name = 'passenger'"
            )
            passenger_ids = [row[0] for row in cur.fetchall()]
            if not passenger_ids:
                raise ValueError("No passengers found in DB")

            # Fetch existing drivers with their vehicle and user info
            cur.execute(
                "SELECT d.id, d.user_id, v.id, v.number_of_seats "
                "FROM driver_data d "
                "JOIN vehicles v ON v.driver_id = d.id"
            )
            drivers = cur.fetchall()
            if not drivers:
                raise ValueError("No drivers found in DB")

            trip_count = 0

            for driver_id, user_id, vehicle_id, max_seats in drivers:

                for _ in range(upcoming_trips):
                    start = random_ville()
                    end = random_ville()
                    trip_id = str(uuid4())
                    start_time = fake.date_time_between(start_date="+1d", end_date="+30d")
                    price = random.randint(5, 15)

                    cur.execute(
                        """
                        INSERT INTO trips (
                            id, driver_id, vehicle_id,
                            start_location, end_location,
                            start_time, price, status
                        ) VALUES (
                            %s, %s, %s,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            %s, %s, (SELECT id FROM trip_status WHERE name = 'upcoming')
                        )""",
                        (trip_id, driver_id, vehicle_id,
                         start["lng"], start["lat"],
                         end["lng"], end["lat"],
                         start_time, price),
                    )

                    num_passengers = random.randint(1, min(3, max_seats))
                    chosen = random.sample(passenger_ids, min(num_passengers, len(passenger_ids)))
                    for pid in chosen:
                        cur.execute(
                            "INSERT INTO trip_passengers (trip_id, user_id) VALUES (%s, %s)",
                            (trip_id, pid),
                        )
                    trip_count += 1

                for _ in range(completed_trips):
                    start = random_ville()
                    end = random_ville()
                    trip_id = str(uuid4())
                    start_time = fake.date_time_between(start_date="-30d", end_date="-1d")
                    price = random.randint(5, 15)
                    completed_at = start_time

                    cur.execute(
                        """
                        INSERT INTO trips (
                            id, driver_id, vehicle_id,
                            start_location, end_location,
                            start_time, price, status, completed_at
                        ) VALUES (
                            %s, %s, %s,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            %s, %s, (SELECT id FROM trip_status WHERE name = 'completed'), %s
                        ) RETURNING id""",
                        (trip_id, driver_id, vehicle_id,
                         start["lng"], start["lat"],
                         end["lng"], end["lat"],
                         start_time, price, completed_at),
                    )
                    trip_id = cur.fetchone()[0]

                    num_passengers = random.randint(1, min(3, max_seats))
                    chosen = random.sample(passenger_ids, min(num_passengers, len(passenger_ids)))

                    for pid in chosen:
                        cur.execute(
                            "INSERT INTO trip_passengers (trip_id, user_id) VALUES (%s, %s)",
                            (trip_id, pid),
                        )
                        cur.execute(
                            """
                            INSERT INTO transactions (
                                tx_from, tx_to, amount, trip_id, completed_at, status
                            ) VALUES (%s, %s, %s, %s, %s, (SELECT id FROM tx_status WHERE name = 'completed'))
                            """,
                            (pid, user_id, price, trip_id, completed_at),
                        )
                        cur.execute("UPDATE platform_balance SET balance = balance + 2")

                    for pid in chosen:
                        comment = fake.sentence()
                        evaluation = random.choice(["positive", "negative"])
                        moderated = random.choice([False, True])
                        driver_rating = random.randint(3, 5) if evaluation == "positive" else random.randint(1, 2)
                        review_ok = current_app.mongo_store.add_trip_review(
                            trip_id=trip_id,
                            driver_id=driver_id,
                            passenger_id=pid,
                            trip_evaluation=evaluation,
                            driver_rating=driver_rating,
                            review_comment=comment,
                            moderated=moderated,
                        )
                        if not review_ok:
                            raise Exception("REVIEW ERROR")

                    trip_count += 1

        return trip_count
    except Exception as e:
        logger.error(f"SEED TRIPS ERROR: {e}")
        raise
