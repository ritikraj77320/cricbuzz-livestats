from src.database.connection import get_db_connection


def main():
    tables = [
        "teams",
        "players",
        "venues",
        "series",
        "matches",
        "innings",
        "batting_performances",
        "bowling_performances",
        "fielding_performances",
        "batting_partnerships",
    ]

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} rows")


if __name__ == "__main__":
    main()