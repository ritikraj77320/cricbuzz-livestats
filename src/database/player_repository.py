
"""Database operations for managing cricket players."""

from src.database.connection import get_db_connection


def create_player(
    player_name: str,
    role: str | None = None,
    date_of_birth: str | None = None,
) -> int:
    """Create a player and return the new player ID."""
    player_name = player_name.strip()

    if not player_name:
        raise ValueError("Player name cannot be empty.")

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO players (
                    player_name,
                    role,
                    date_of_birth
                )
                VALUES (%s, %s, %s)
                RETURNING player_id;
                """,
                (player_name, role, date_of_birth),
            )
            player_id = cursor.fetchone()[0]

        connection.commit()
        return player_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_players(
    search: str = "",
    limit: int = 100,
):
    """Retrieve players, optionally filtering by name."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("Limit must be an integer.")

    if not 1 <= limit <= 1000:
        raise ValueError("Limit must be between 1 and 1000.")

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    player_id,
                    player_name,
                    role,
                    date_of_birth,
                    provider_player_id
                FROM players
                WHERE player_name ILIKE %s
                ORDER BY player_name ASC
                LIMIT %s;
                """,
                (f"%{search.strip()}%", limit),
            )

            columns = [description.name for description in cursor.description]
            rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    finally:
        connection.close()


def update_player(
    player_id: int,
    player_name: str,
    role: str | None = None,
    date_of_birth: str | None = None,
) -> bool:
    """Update a player's details. Return True if found."""
    player_name = player_name.strip()

    if not player_name:
        raise ValueError("Player name cannot be empty.")

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE players
                SET
                    player_name = %s,
                    role = %s,
                    date_of_birth = %s
                WHERE player_id = %s
                RETURNING player_id;
                """,
                (player_name, role, date_of_birth, player_id),
            )
            updated = cursor.fetchone() is not None

        connection.commit()
        return updated

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def delete_player(player_id: int) -> bool:
    """Delete a player. Return True if found and deleted."""
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM players
                WHERE player_id = %s
                RETURNING player_id;
                """,
                (player_id,),
            )
            deleted = cursor.fetchone() is not None

        connection.commit()
        return deleted

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
