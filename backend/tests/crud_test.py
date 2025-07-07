from db_store.crud import test_connection

if __name__ == "__main__":
    if test_connection():
        print("Database connection successful.")
    else:
        print("Database connection failed.")

