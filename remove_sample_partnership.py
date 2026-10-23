
from src.database.connection import get_db_connection

connection = get_db_connection()

try:
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM batting_partnerships AS bp
            USING players AS p1, players AS p2
            WHERE bp.batter1_id = p1.player_id
              AND bp.batter2_id = p2.player_id
              AND p1.player_name = %s
              AND p2.player_name = %s
            RETURNING bp.partnership_id;
        """, ("Sample Batter India", "Sample Bowler India"))

        deleted_rows = cursor.fetchall()
        connection.commit()

        print("Deleted sample partnership IDs:", deleted_rows)
        print("Number of records deleted:", len(deleted_rows))

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
