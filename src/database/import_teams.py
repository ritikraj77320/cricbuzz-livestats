import json
from pathlib import Path

from src.api.match_parser import extract_matches
from src.database.connection import get_db_connection


def import_teams():
    file_path = Path("data/raw/live_matches.json")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    matches = extract_matches(data)
    teams = {}

    for match in matches:
        for team_id, team_name in [
            (match["team1_id"], match["team1_name"]),
            (match["team2_id"], match["team2_name"]),
        ]:
            if team_id is not None and team_name:
                teams[str(team_id)] = team_name

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            for provider_id, team_name in teams.items():
                cursor.execute(
                    """
                    SELECT team_id
                    FROM teams
                    WHERE provider_team_id = %s
                    """,
                    (provider_id,),
                )

                if cursor.fetchone():
                    continue

                cursor.execute(
                    """
                    SELECT team_id
                    FROM teams
                    WHERE team_name = %s
                    """,
                    (team_name,),
                )
                existing_team = cursor.fetchone()

                if existing_team:
                    cursor.execute(
                        """
                        UPDATE teams
                        SET provider_team_id = %s
                        WHERE team_id = %s
                          AND provider_team_id IS NULL
                        """,
                        (provider_id, existing_team[0]),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO teams (team_name, provider_team_id)
                        VALUES (%s, %s)
                        ON CONFLICT (provider_team_id) DO NOTHING
                        """,
                        (team_name, provider_id),
                    )

    print(f"Team records processed: {len(teams)}")
    print("Team provider-ID mapping completed.")


if __name__ == "__main__":
    import_teams()