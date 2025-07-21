from psycopg.rows import dict_row


def get_driver_data(conn, user_id):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT id, rating WHERE user_id = %s",
            (user_id,),
        )
        driver_data = cur.fetchall()
        return driver_data if driver_data else None


def set_driver_preferences(conn, driver_id, preferences):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM driver_preferences WHERE driver_id = %s", (driver_id,))
        for preference in preferences:
            cur.execute(
                "INSERT INTO driver_preferences (driver_id, preference_id) VALUES (%s, %s)",
                (driver_id, preference["id"]),
            )
        conn.commit()
        return True


def get_driver_preferences(conn, driver_id):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT p.name FROM preferences p JOIN driver_preferences dp ON dp.preference_id = p.id WHERE dp.driver_id = %s",
            (driver_id,),
        )
        current_preferences = cur.fetchall()
        return current_preferences if current_preferences else None


def add_vehicle(conn, driver_id, vehicle_data):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO vehicles (driver_id, model, registration_date, plate_number, color, number_of_seats, brand, energy_type_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                driver_id,
                vehicle_data["model"],
                vehicle_data["registration_date"],
                vehicle_data["plate_number"],
                vehicle_data["color"],
                vehicle_data["number_of_seats"],
                vehicle_data["brand"],
                vehicle_data["energy_type_id"],
            ),
        )
        conn.commit()
        return True


def get_driver_vehicles(conn, driver_id):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT v.id, v.model, v.registration_date, v.plate_number, v.color, v.number_of_seats, b.name AS brand, e.name AS energy_type FROM vehicles v JOIN vehicle_brand b ON v.brand = b.id JOIN energy_types e ON v.energy_type_id = e.id WHERE v.driver_id = %s",
            (driver_id,),
        )
        vehicles = cur.fetchall()
        return vehicles if vehicles else None


def set_driver_rating(conn, driver_id):
    with conn.cursor as cur:
        # select rating from trips where driver_id = driver_id
        # set driver rating as average of all trips rating
        cur.execute("SELECT rating FROM trips WHERE driver_id = %s", (driver_id,))
        all_ratings = cur.fetchall()
        average = sum(x for int(x) in all_ratings) / len(all_ratings)

        cur.execute(
            "UPDATE driver_data SET rating = %s WHERE user_id = %s",
            (average, driver_id),
        )
        conn.commit()
