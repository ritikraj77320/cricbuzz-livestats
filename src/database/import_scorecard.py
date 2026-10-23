
"""Fetch Cricbuzz scorecards and import player performances into PostgreSQL."""

from src.api.api_client import get_live_matches, get_match_scorecard
from src.api.scorecard_parser import parse_scorecard
from src.database.connection import get_db_connection


def extract_live_match_ids(data):
    """Extract match IDs from the Cricbuzz live-match response."""
    match_ids = set()

    for match_type in data.get("typeMatches", []):
        for series_match in match_type.get("seriesMatches", []):
            wrapper = series_match.get("seriesAdWrapper", {})

            for match in wrapper.get("matches", []):
                match_info = match.get("matchInfo", {})
                match_id = match_info.get("matchId")

                if match_id is not None:
                    match_ids.add(str(match_id))

    return sorted(match_ids)


def get_or_create_player(cursor, player):
    """Find or insert a player using the Cricbuzz player ID."""
    provider_player_id = player.get("provider_player_id")
    player_name = (player.get("player_name") or "").strip()

    if not provider_player_id or not player_name:
        raise ValueError("Player ID and player name are required.")

    cursor.execute(
        """
        INSERT INTO players (player_name, provider_player_id)
        VALUES (%s, %s)
        ON CONFLICT (provider_player_id)
        DO UPDATE SET player_name = EXCLUDED.player_name
        RETURNING player_id;
        """,
        (player_name, str(provider_player_id)),
    )

    return cursor.fetchone()[0]


def import_one_scorecard(match_provider_id):
    """Fetch and import one match's scorecard."""
    raw_data = get_match_scorecard(match_provider_id)
    import json

    with open(
        "data/raw/debug_scorecard.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(raw_data, file, indent=2, ensure_ascii=False)

    print("Raw scorecard saved successfully.")
    scorecard = parse_scorecard(raw_data)
    innings_data = scorecard.get("innings", [])

    if not innings_data:
        print(f"No innings available for match {match_provider_id}.")
        return False

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT match_id
                FROM matches
                WHERE provider_match_id = %s;
                """,
                (str(match_provider_id),),
            )
            match_row = cursor.fetchone()

            if match_row is None:
                print(
                    f"Match {match_provider_id} is not in PostgreSQL. "
                    "Skipping scorecard import."
                )
                connection.rollback()
                return False

            match_id = match_row[0]
            batting_count = 0
            bowling_count = 0
            partnership_count = 0
            fielding_count = 0
            innings_count = 0
            for innings_number, inning in enumerate(innings_data, start=1):
                batting_team = (inning.get("batting_team") or "").strip()

                cursor.execute(
                    """
                    SELECT team_id
                    FROM teams
                    WHERE LOWER(TRIM(team_name)) = LOWER(%s);
                    """,
                    (batting_team,),
                )
                team_row = cursor.fetchone()

                if team_row is None:
                    raise ValueError(
                        f"Team '{batting_team}' was not found in PostgreSQL. "
                        "Sync teams before importing scorecards."
                    )

                batting_team_id = team_row[0]

                cursor.execute(
                    """
                    INSERT INTO innings (
                        match_id, batting_team_id, innings_number,
                        total_runs, wickets, legal_balls, extras
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (match_id, innings_number)
                    DO UPDATE SET
                        batting_team_id = EXCLUDED.batting_team_id,
                        total_runs = EXCLUDED.total_runs,
                        wickets = EXCLUDED.wickets,
                        legal_balls = EXCLUDED.legal_balls,
                        extras = EXCLUDED.extras
                    RETURNING innings_id;
                    """,
                    (
                        match_id,
                        batting_team_id,
                        innings_number,
                        inning.get("team_score", 0),
                        inning.get("wickets", 0),
                        inning.get("legal_balls", 0),
                        (inning.get("extras") or {}).get("total", 0),
                    ),
                )

                innings_id = cursor.fetchone()[0]
                innings_count += 1
                # Remove old performance records for this innings.
                # The latest scorecard data will be inserted below.
                cursor.execute(
                    """
                    DELETE FROM batting_performances
                    WHERE innings_id = %s;
                    """,
                    (innings_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM bowling_performances
                    WHERE innings_id = %s;
                    """,
                    (innings_id,),
                )
                               
                cursor.execute(
                    """
                    DELETE FROM batting_partnerships
                    WHERE innings_id = %s;
                    """,
                    (innings_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM fielding_performances
                    WHERE innings_id = %s;
                    """,
                    (innings_id,),
                )


                for batter in inning.get("batting", []):
                    # Skip players who have not yet batted.
                    if (
                        not batter.get("dismissal")
                        and not batter.get("balls_faced", 0)
                        and not batter.get("runs", 0)
                    ):
                        continue

                    player_id = get_or_create_player(cursor, batter)
                    dismissal = (batter.get("dismissal") or "").strip()

                    if dismissal.lower() == "batting":
                        dismissal = None

                    cursor.execute(
                        """
                        INSERT INTO batting_performances (
                            innings_id, player_id, runs, balls_faced,
                            fours, sixes, dismissal
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (innings_id, player_id)
                        DO UPDATE SET
                            runs = EXCLUDED.runs,
                            balls_faced = EXCLUDED.balls_faced,
                            fours = EXCLUDED.fours,
                            sixes = EXCLUDED.sixes,
                            dismissal = EXCLUDED.dismissal;
                        """,
                        (
                            innings_id,
                            player_id,
                            batter.get("runs", 0),
                            batter.get("balls_faced", 0),
                            batter.get("fours", 0),
                            batter.get("sixes", 0),
                            dismissal or None,
                        ),
                    )
                    batting_count += 1

                for bowler in inning.get("bowling", []):
                    player_id = get_or_create_player(cursor, bowler)

                    cursor.execute(
                        """
                        INSERT INTO bowling_performances (
                            innings_id, player_id, legal_balls,
                            maidens, runs_conceded, wickets, economy
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (innings_id, player_id)
                        DO UPDATE SET
                            legal_balls = EXCLUDED.legal_balls,
                            maidens = EXCLUDED.maidens,
                            runs_conceded = EXCLUDED.runs_conceded,
                            wickets = EXCLUDED.wickets,
                            economy = EXCLUDED.economy;
                        """,
                        (
                            innings_id,
                            player_id,
                            bowler.get("legal_balls", 0),
                            bowler.get("maidens", 0),
                            bowler.get("runs_conceded", 0),
                            bowler.get("wickets", 0),
                            bowler.get("economy", 0),
                        ),
                    )
                    bowling_count += 1

                
                # Aggregate contributions so each fielder gets one row
                # per innings.
                fielding_totals = {}

                for contribution in inning.get("fielding", []):
                    fielder_name = (
                        contribution.get("fielder_name") or ""
                    ).strip()

                    # Normalize substitute-player notation.
                    if fielder_name.lower().startswith("(sub)"):
                        fielder_name = fielder_name[5:].strip()

                    if not fielder_name:
                        continue

                    contribution_type = contribution.get(
                        "contribution_type"
                    )

                    if contribution_type not in {
                        "catch", "stumping", "run_out"
                    }:
                        continue

                    cursor.execute(
                        """
                        SELECT player_id
                        FROM players
                        WHERE LOWER(TRIM(player_name)) = LOWER(%s)
                        ORDER BY
                            CASE
                                WHEN provider_player_id IS NULL THEN 1
                                ELSE 0
                            END,
                            player_id
                        LIMIT 1;
                        """,
                        (fielder_name,),
                    )
                    player_row = cursor.fetchone()

                    if player_row is None:
                        cursor.execute(
                            """
                            INSERT INTO players (player_name)
                            VALUES (%s)
                            RETURNING player_id;
                            """,
                            (fielder_name,),
                        )
                        player_row = cursor.fetchone()

                    fielder_id = player_row[0]

                    if fielder_id not in fielding_totals:
                        fielding_totals[fielder_id] = {
                            "catches": 0,
                            "stumpings": 0,
                            "run_outs": 0,
                        }

                    if contribution_type == "catch":
                        fielding_totals[fielder_id]["catches"] += 1
                    elif contribution_type == "stumping":
                        fielding_totals[fielder_id]["stumpings"] += 1
                    elif contribution_type == "run_out":
                        fielding_totals[fielder_id]["run_outs"] += 1

                for fielder_id, totals in fielding_totals.items():
                    cursor.execute(
                        """
                        INSERT INTO fielding_performances (
                            innings_id,
                            player_id,
                            catches,
                            stumpings,
                            run_outs
                        )
                        VALUES (%s, %s, %s, %s, %s);
                        """,
                        (
                            innings_id,
                            fielder_id,
                            totals["catches"],
                            totals["stumpings"],
                            totals["run_outs"],
                        ),
                    )

                    fielding_count += 1


                    
                for partnership_number, partnership in enumerate(
                    inning.get("partnerships", []), start=1
                ):
                    batter1 = {
                        "provider_player_id":
                            partnership.get("batter1_provider_id"),
                        "player_name":
                            partnership.get("batter1_name"),
                    }
                    batter2 = {
                        "provider_player_id":
                            partnership.get("batter2_provider_id"),
                        "player_name":
                            partnership.get("batter2_name"),
                    }

                    batter1_id = get_or_create_player(cursor, batter1)
                    batter2_id = get_or_create_player(cursor, batter2)

                    cursor.execute(
                        """
                        INSERT INTO batting_partnerships (
                            innings_id,
                            batter1_id,
                            batter2_id,
                            partnership_runs,
                            partnership_balls,
                            partnership_number
                        )
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """,
                        (
                            innings_id,
                            batter1_id,
                            batter2_id,
                            partnership.get("partnership_runs", 0),
                            partnership.get("partnership_balls", 0),
                            partnership_number,
                        ),
                    )

                    partnership_count += 1

        connection.commit()

        print(f"\nScorecard imported: {match_provider_id}")
        print(f"Innings: {innings_count}")
        print(f"Batting records: {batting_count}")
        print(f"Bowling records: {bowling_count}")
        print(f"Partnership records: {partnership_count}")
        print(f"Fielding records: {fielding_count}")

        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def import_live_scorecards():
    """Fetch and import scorecards for matches in the live-match response."""
    live_data = get_live_matches()
    match_ids = extract_live_match_ids(live_data)

    if not match_ids:
        print("No match IDs found in the Cricbuzz live-match response.")
        return

    imported = 0
    skipped_or_failed = 0

    print(f"Found {len(match_ids)} match IDs in the live-match response.")

    for match_id in match_ids:
        try:
            if import_one_scorecard(match_id):
                imported += 1
            else:
                skipped_or_failed += 1

        except Exception as error:
            skipped_or_failed += 1
            print(
                f"Scorecard import failed for match {match_id}: "
                f"{type(error).__name__}: {error}"
            )

    print("\nScorecard import summary")
    print(f"Successfully imported: {imported}")
    print(f"Skipped or failed: {skipped_or_failed}")


if __name__ == "__main__":
    import_live_scorecards()