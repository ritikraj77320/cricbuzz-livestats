import json
from datetime import datetime, timezone
from pathlib import Path

from src.database.connection import get_db_connection


def to_timestamp(value):
    """Convert an API millisecond timestamp to a timezone-aware datetime."""
    if value is None:
        return None

    try:
        return datetime.fromtimestamp(
            int(value) / 1000,
            tz=timezone.utc,
        )
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def extract_match_records(data):
    """Extract match records from the saved Cricbuzz response."""
    records = []

    for match_type in data.get("typeMatches", []):
        for group in match_type.get("seriesMatches", []):
            wrapper = group.get("seriesAdWrapper", {})

            for match in wrapper.get("matches", []):
                info = match.get("matchInfo", {})
                if not info or info.get("matchId") is None:
                    continue

                team1 = info.get("team1", {})
                team2 = info.get("team2", {})
                venue = info.get("venueInfo", {})

                records.append({
                    "provider_match_id": str(info["matchId"]),
                    "provider_series_id": str(info["seriesId"])
                    if info.get("seriesId") is not None else None,
                    "provider_team1_id": str(team1["teamId"])
                    if team1.get("teamId") is not None else None,
                    "provider_team2_id": str(team2["teamId"])
                    if team2.get("teamId") is not None else None,
                    "provider_venue_id": str(venue["id"])
                    if venue.get("id") is not None else None,
                    "match_name": info.get("matchDesc"),
                    "match_format": info.get("matchFormat"),
                    "start_time": to_timestamp(info.get("startDate")),
                    "status": info.get("state"),
                })

    return records


def import_matches():
    file_path = Path("data/raw/live_matches.json")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    records = extract_match_records(data)
    imported = 0
    skipped = 0

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            for record in records:
                cursor.execute(
                    """
                    SELECT team_id
                    FROM teams
                    WHERE provider_team_id = %s
                    """,
                    (record["provider_team1_id"],),
                )
                team1 = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT team_id
                    FROM teams
                    WHERE provider_team_id = %s
                    """,
                    (record["provider_team2_id"],),
                )
                team2 = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT series_id
                    FROM series
                    WHERE provider_series_id = %s
                    """,
                    (record["provider_series_id"],),
                )
                series = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT venue_id
                    FROM venues
                    WHERE provider_venue_id = %s
                    """,
                    (record["provider_venue_id"],),
                )
                venue = cursor.fetchone()

                if not team1 or not team2 or not series:
                    skipped += 1
                    print(
                        "Skipped match due to missing team or series mapping:",
                        record["provider_match_id"],
                    )
                    continue

                cursor.execute(
                    """
                    INSERT INTO matches (
                        series_id,
                        venue_id,
                        team1_id,
                        team2_id,
                        match_name,
                        match_format,
                        start_time,
                        status,
                        provider_match_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (provider_match_id)
                    DO UPDATE SET
                        series_id = EXCLUDED.series_id,
                        venue_id = EXCLUDED.venue_id,
                        team1_id = EXCLUDED.team1_id,
                        team2_id = EXCLUDED.team2_id,
                        match_name = EXCLUDED.match_name,
                        match_format = EXCLUDED.match_format,
                        start_time = EXCLUDED.start_time,
                        status = EXCLUDED.status
                    """,
                    (
                        series[0],
                        venue[0] if venue else None,
                        team1[0],
                        team2[0],
                        record["match_name"],
                        record["match_format"],
                        record["start_time"],
                        record["status"],
                        record["provider_match_id"],
                    ),
                )
                imported += 1

    print(f"Match records processed: {len(records)}")
    print(f"Imported or updated: {imported}")
    print(f"Skipped due to missing mappings: {skipped}")


if __name__ == "__main__":
    import_matches()