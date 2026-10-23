
from src.database.connection import get_db_connection

connection = get_db_connection()

try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                bp.partnership_id,
                m.provider_match_id,
                i.innings_number,
                bp.partnership_number,
                p1.player_name AS batter1,
                p2.player_name AS batter2,
                bp.partnership_runs,
                bp.partnership_balls
            FROM batting_partnerships bp
            JOIN innings i
                ON bp.innings_id = i.innings_id
            JOIN matches m
                ON i.match_id = m.match_id
            JOIN players p1
                ON bp.batter1_id = p1.player_id
            JOIN players p2
                ON bp.batter2_id = p2.player_id
            ORDER BY
                m.provider_match_id,
                i.innings_number,
                bp.partnership_number;
        """)

        rows = cursor.fetchall()

        print(f"\nTotal partnership records: {len(rows)}")
        print("\n--- PARTNERSHIP DATA ---")

        for row in rows:
            print(row)

finally:
    connection.close()
