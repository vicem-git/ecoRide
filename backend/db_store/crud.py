import psycopg
import config

db_config = config.db_config


def test_connection():
    """
    Test the connection to the PostgreSQL database using psycopg.
    """
    try:
        with psycopg.connect(
            f"postgresql://{db_config['db_user']}:{db_config['db_password']}@{db_config['db_host']}:{db_config['db_port']}/{db_config['db_name']}"
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
                return result[0] == 1  # Should return True if connection is successful
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def create_user():
    pass
