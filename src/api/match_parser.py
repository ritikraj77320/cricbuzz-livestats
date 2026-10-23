def extract_matches(data):
    """Extract match information from the Cricbuzz matches response."""
    extracted_matches = []

    for match_type in data.get("typeMatches", []):
        for series_group in match_type.get("seriesMatches", []):
            series_wrapper = series_group.get("seriesAdWrapper", {})

            for match in series_wrapper.get("matches", []):
                match_info = match.get("matchInfo", {})

                if not match_info:
                    continue

                team1 = match_info.get("team1", {})
                team2 = match_info.get("team2", {})
                venue = match_info.get("venueInfo", {})

                extracted_matches.append({
                    "match_id": match_info.get("matchId"),
                    "series_id": match_info.get("seriesId"),
                    "series_name": match_info.get("seriesName"),
                    "series_start_date": series_wrapper.get("startDate"),
                    "series_end_date": series_wrapper.get("endDate"),
                    "match_description": match_info.get("matchDesc"),
                    "match_format": match_info.get("matchFormat"),
                    "start_date": match_info.get("startDate"),
                    "state": match_info.get("state"),
                    "status": match_info.get("status"),
                    "team1_id": team1.get("teamId"),
                    "team1_name": team1.get("teamName"),
                    "team2_id": team2.get("teamId"),
                    "team2_name": team2.get("teamName"),
                    "venue_id": venue.get("id"),
                    "venue_name": venue.get("ground"),
                    "venue_city": venue.get("city"),
                    "venue_country": venue.get("country"),
                })

    return extracted_matches