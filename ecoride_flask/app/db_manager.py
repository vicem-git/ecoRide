from psycopg_pool import pool


class DatabaseManager:
    def __init__(self, db_config):
        self.pool = pool.ConnectionPool(
            min_size=db_config["min_conn"],
            max_size=db_config["max_conn"],
            conninfo=f"postgresql://{db_config['db_user']}:{db_config['db_password']}@{db_config['db_host']}:{db_config['db_port']}/{db_config['db_name']}",
        )

    def get_connection(self):
        return self.pool.getconn()

    def release_connection(self, conn):
        self.pool.putconn(conn)

    def close_all(self):
        self.pool.closeall()
