-- CREATE ROLE ecoride_admin WITH LOGIN PASSWORD 'your_secure_password';
-- CREATE DATABASE ecoride_db OWNER ecoride_admin;
-- GRANT ALL PRIVILEGES ON DATABASE ecoride_db TO ecoride_admin;
-- \c ecoride_db
CREATE SCHEMA IF NOT EXISTS public;
GRANT USAGE, CREATE ON SCHEMA public TO ecoride_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO ecoride_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO ecoride_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO ecoride_admin;


CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";

SET TIME ZONE 'Europe/Paris';

CREATE TABLE platform_balance (
  id BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (id),
  balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0)
);

INSERT INTO platform_balance (id, balance) VALUES (TRUE, 0)
ON CONFLICT DO NOTHING;

CREATE TABLE account_access_type (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO account_access_type (name) VALUES
('user'),
('admin'),
('moderator');


CREATE TABLE account_status (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO account_status (name) VALUES
('active'),
('suspended');


CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    access_type UUID NOT NULL REFERENCES account_access_type(id), 
    status UUID NOT NULL REFERENCES account_status(id),
    created_at TIMESTAMP DEFAULT now()
);


CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO roles (name) VALUES
('driver'),
('passenger');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID UNIQUE NOT NULL REFERENCES accounts(id) ON DELETE SET NULL,
    username VARCHAR(30) UNIQUE NOT NULL,
    photo_url VARCHAR(255) NULL,
    credits INTEGER DEFAULT 20 CHECK (credits >= 0)
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);


CREATE TABLE preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO preferences (name) VALUES
('smoking_allowed'),
('non_smoking'),
('pets_allowed'),
('no_pets_allowed'),
('music_allowed'),
('no_music_allowed'),
('air_conditioning'),
('no_air_conditioning');

CREATE TABLE driver_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER DEFAULT 0 CHECK (rating >= 0 AND rating <= 5)
);

CREATE TABLE driver_preferences (
  driver_id UUID NOT NULL REFERENCES driver_data(id) ON DELETE CASCADE,
  preference_id UUID NOT NULL REFERENCES preferences(id) ON DELETE CASCADE,
  PRIMARY KEY (driver_id, preference_id)
);

CREATE TABLE vehicle_brand (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO vehicle_brand (name) VALUES
('Acura'),
('Audi'),
('BMW'),
('BYD'),
('Chevrolet'),
('Chrysler'),
('Citroen'),
('Dodge'),
('Fiat'),
('Ford'),
('GMC'),
('Honda'),
('Hyundai'),
('Infiniti'),
('Jaguar'),
('Jeep'),
('Kia'),
('Land Rover'),
('Lexus'),
('Lincoln'),
('Mazda'),
('Mercedes-Benz'),
('Mitsubishi'),
('Nissan'),
('Opel'),
('Peugeot'),
('Polestar'),
('Porsche'),
('Renault'),
('Skoda'),
('Subaru'),
('Suzuki'),
('Tesla'),
('Toyota'),
('Volkswagen'),
('Volvo');

CREATE TABLE energy_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO energy_types (name) VALUES
('essence'),
('diesel'),
('electrique'),
('hybrid');

CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    driver_id UUID NOT NULL REFERENCES driver_data(id) ON DELETE CASCADE,
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    registration_date DATE NOT NULL,
    brand UUID NOT NULL REFERENCES vehicle_brand(id) ON DELETE CASCADE,
    model VARCHAR(50) NOT NULL,
    color VARCHAR(30) NOT NULL,
    photo_url VARCHAR(255) NULL,
    number_of_seats INTEGER NOT NULL,
    energy_type UUID NOT NULL REFERENCES energy_types(id) ON DELETE CASCADE
);

CREATE TABLE trip_status (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO trip_status (name) values
('upcoming'),
('in_progress'),
('completed'),
('cancelled');

CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    driver_id UUID NOT NULL REFERENCES driver_data(id) ON DELETE CASCADE,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    start_location GEOGRAPHY(POINT, 4326) NOT NULL,
    end_location GEOGRAPHY(POINT, 4326) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    price INTEGER NOT NULL,
    status UUID NOT NULL REFERENCES trip_status(id) ON DELETE CASCADE,
    rating INTEGER DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    completed_at TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON trips
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE OR REPLACE FUNCTION mark_trip_completed_at()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status IN (
    (SELECT id FROM trip_status WHERE name = 'completed'),
    (SELECT id FROM trip_status WHERE name = 'cancelled')
  ) AND OLD.status IS DISTINCT FROM NEW.status THEN
    NEW.completed_at := now();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_mark_trip_completed_at
BEFORE UPDATE ON trips
FOR EACH ROW
EXECUTE FUNCTION mark_trip_completed_at();


CREATE TABLE trip_passengers (
  trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY (trip_id, user_id)
);

CREATE OR REPLACE VIEW trip_owner AS
SELECT
    t.id AS trip_id,
    u.id AS user_id
FROM
    trips t
JOIN driver_data d ON t.driver_id = d.id
JOIN users u ON d.user_id = u.id;

CREATE OR REPLACE VIEW trip_passengers_userdata AS
SELECT
    tp.trip_id,
    u.id, u.username AS user_id,
    u.username,
    a.email
FROM
    trip_passengers tp
JOIN users u ON tp.user_id = u.id
JOIN accounts a ON u.account_id = a.id;

CREATE TABLE tx_status (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO tx_status (name) VALUES
('completed'),
('pending'),
('refunded');

CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tx_from UUID NOT NULL REFERENCES users(id),
  tx_to UUID NOT NULL REFERENCES users(id),
  amount INTEGER NOT NULL CHECK (amount > 0),
  trip_id UUID NOT NULL REFERENCES trips(id),
  status UUID NOT NULL REFERENCES tx_status(id),
  completed_at TIMESTAMP DEFAULT NULL,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE OR REPLACE FUNCTION mark_tx_completed_at()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status IN (
    (SELECT id FROM tx_status WHERE name = 'completed'),
    (SELECT id FROM tx_status WHERE name = 'refunded')
  ) AND OLD.status IS DISTINCT FROM NEW.status THEN
    NEW.completed_at := now();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_mark_tx_completed_at
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION mark_tx_completed_at();


CREATE TABLE trip_txs (
  trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
  tx_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
  priMARY KEY (trip_id, tx_id)
);

CREATE OR REPLACE VIEW trip_available_seats AS
SELECT
  t.id AS trip_id,
  v.number_of_seats - COUNT(tp.user_id) AS available_seats
FROM trips t
JOIN vehicles v ON v.id = t.vehicle_id
LEFT JOIN trip_passengers tp ON tp.trip_id = t.id
GROUP BY t.id, v.number_of_seats;

CREATE TABLE review_status (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO review_status (name) VALUES
('pending'),
('approved'),
('rejected');

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 0 AND rating <= 5) NOT NULL,
    comments TEXT,
    review_status_id UUID NOT NULL REFERENCES review_status(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TABLE trip_summaries (
    trip_id UUID PRIMARY KEY REFERENCES trips(id) ON DELETE CASCADE,
    summary JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE VIEW trip_with_status_and_summary AS
SELECT
  t.id AS trip_id,
  t.driver_id,
  s.name AS status,
  ts.summary
FROM trips t
JOIN trip_status s ON t.status = s.id
LEFT JOIN trip_summaries ts ON ts.trip_id = t.id;

CREATE OR REPLACE VIEW trip_summaries_asst AS
SELECT
  twss.trip_id,
  twss.driver_id,
  twss.status,
  twss.summary,
  tas.available_seats
FROM trip_with_status_and_summary twss
JOIN trip_available_seats tas ON twss.trip_id = tas.trip_id;



