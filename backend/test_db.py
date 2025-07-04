import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv("../.env")

engine = create_engine(
    f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

inspector = inspect(engine)
tables = inspector.get_table_names(schema="public")
print("Tables in DB:", tables)
