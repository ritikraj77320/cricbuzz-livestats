from src.database.connection import get_db_connection


def main():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database(), version()")
                database_name, version = cursor.fetchone()

                print("Database connection successful!")
                print("Database:", database_name)
                print("PostgreSQL version:", version.split(",")[0])

    except Exception as error:
        print("Database connection failed:", type(error).__name__)
        print("Details:", error)


if __name__ == "__main__":
    main()