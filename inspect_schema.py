
from src.database.connection import get_db_connection


def inspect_schema():
    """Print all public PostgreSQL table columns."""
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    table_name,
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
                """
            )

            rows = cursor.fetchall()

            for table_name, column_name, data_type in rows:
                print(f"{table_name}.{column_name} ({data_type})")

    finally:
        connection.close()


if __name__ == "__main__":
    inspect_schema()
