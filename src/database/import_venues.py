import json
from pathlib import Path

from src.api.match_parser import extract_matches
from src.database.connection import get_db_connection


def import_venues():
    file_path = Path("data/raw/live_matches.json")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    matches = extract_matches(data)
    venues = {}

    for match in matches:
        venue_id = match.get("venue_id")
        venue_name = match.get("venue_name")
        venue_city = match.get("venue_city")
        venue_country = match.get("venue_country")

        if venue_name:
            key = str(venue_id) if venue_id is not None else venue_name
            venues[key] = {
                "provider_id": str(venue_id) if venue_id is not None else None,
                "name": venue_name,
                "city": venue_city,
                "country": venue_country,
            }

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            for venue in venues.values():
                provider_id = venue["provider_id"]

                if provider_id:
                    cursor.execute(
                        """
                        SELECT venue_id
                        FROM venues
                        WHERE provider_venue_id = %s
                        """,
                        (provider_id,),
                    )

                    if cursor.fetchone():
                        continue

                cursor.execute(
                    """
                    SELECT venue_id
                    FROM venues
                    WHERE venue_name = %s
                      AND city IS NOT DISTINCT FROM %s
                    """,
                    (venue["name"], venue["city"]),
                )

                existing = cursor.fetchone()

                if existing:
                    if provider_id:
                        cursor.execute(
                            """
                            UPDATE venues
                            SET provider_venue_id = %s
                            WHERE venue_id = %s
                              AND provider_venue_id IS NULL
                            """,
                            (provider_id, existing[0]),
                        )
                    continue

                cursor.execute(
                    """
                    INSERT INTO venues (
                        venue_name,
                        city,
                        country,
                        provider_venue_id
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (provider_venue_id) DO NOTHING
                    """,
                    (
                        venue["name"],
                        venue["city"],
                        venue["country"],
                        provider_id,
                    ),
                )

    print(f"Venue records processed: {len(venues)}")
    print("Venue import completed.")


if __name__ == "__main__":
    import_venues()