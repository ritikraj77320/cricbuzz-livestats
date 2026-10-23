import json
from datetime import datetime, timezone
from pathlib import Path

from src.database.connection import get_db_connection


def to_date(value):
    """Convert a millisecond timestamp to a date."""
    if value is None:
        return None

    try:
        timestamp = int(value) / 1000
        return datetime.fromtimestamp(
            timestamp, tz=timezone.utc
        ).date()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def extract_series(data):
    """Extract unique series records from the matches response."""
    series_records = {}

    for match_type in data.get("typeMatches", []):
        for series_group in match_type.get("seriesMatches", []):
            wrapper = series_group.get("seriesAdWrapper", {})

            if not wrapper:
                continue

            series_id = wrapper.get("seriesId")
            series_name = wrapper.get("seriesName")

            if series_id is None or not series_name:
                continue

            series_records[str(series_id)] = {
                "provider_id": str(series_id),
                "name": series_name,
                "start_date": to_date(wrapper.get("startDate")),
                "end_date": to_date(wrapper.get("endDate")),
            }

    return series_records


def import_series():
    file_path = Path("data/raw/live_matches.json")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    series_records = extract_series(data)

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            for series in series_records.values():
                cursor.execute(
                    """
                    SELECT series_id
                    FROM series
                    WHERE provider_series_id = %s
                    """,
                    (series["provider_id"],),
                )

                existing = cursor.fetchone()

                if existing:
                    cursor.execute(
                        """
                        UPDATE series
                        SET series_name = %s,
                            start_date = %s,
                            end_date = %s
                        WHERE series_id = %s
                        """,
                        (
                            series["name"],
                            series["start_date"],
                            series["end_date"],
                            existing[0],
                        ),
                    )
                    continue

                cursor.execute(
                    """
                    SELECT series_id
                    FROM series
                    WHERE series_name = %s
                    """,
                    (series["name"],),
                )

                existing = cursor.fetchone()

                if existing:
                    cursor.execute(
                        """
                        UPDATE series
                        SET provider_series_id = %s
                        WHERE series_id = %s
                          AND provider_series_id IS NULL
                        """,
                        (series["provider_id"], existing[0]),
                    )
                    continue

                cursor.execute(
                    """
                    INSERT INTO series (
                        series_name,
                        start_date,
                        end_date,
                        provider_series_id
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (provider_series_id) DO NOTHING
                    """,
                    (
                        series["name"],
                        series["start_date"],
                        series["end_date"],
                        series["provider_id"],
                    ),
                )

    print(f"Series records processed: {len(series_records)}")
    print("Series import completed.")


if __name__ == "__main__":
    import_series()