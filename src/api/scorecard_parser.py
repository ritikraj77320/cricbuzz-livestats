
"""Parse Cricbuzz scorecard JSON into structured Python data."""


def _to_int(value, default=0):
    """Convert a value to an integer safely."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value, default=0.0):
    """Convert a value to a float safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default\


def _parse_fielding_dismissal(dismissal):
    """
    Extract fielding contributions from a batter's dismissal text.

    Returns a dictionary with the fielder name and contribution type,
    or None when the dismissal does not identify a fielding contribution.
    """
    if not isinstance(dismissal, str):
        return None

    text = dismissal.strip()
    lower_text = text.lower()

    if not text or lower_text in {"not out", "retired hurt", "absent hurt"}:
        return None

    # Caught: c Fielder b Bowler
    if lower_text.startswith("c ") and " b " in lower_text:
        fielder = text[2:text.lower().rfind(" b ")].strip()

        if fielder:
            return {
                "fielder_name": fielder,
                "contribution_type": "catch",
            }

    # Run out: run out (Fielder)
    if lower_text.startswith("run out"):
        start = text.find("(")
        end = text.rfind(")")

        if start != -1 and end > start:
            fielder = text[start + 1:end].strip()

            if fielder:
                return {
                    "fielder_name": fielder,
                    "contribution_type": "run_out",
                }

    # Stumped: st Fielder b Bowler
    if lower_text.startswith("st ") and " b " in lower_text:
        fielder = text[3:text.lower().rfind(" b ")].strip()

        if fielder:
            return {
                "fielder_name": fielder,
                "contribution_type": "stumping",
            }

    return None



def parse_scorecard(data):
    """
    Extract match status, innings totals, batting, bowling and extras.

    Args:
        data: Parsed JSON dictionary from the scorecard API.

    Returns:
        A dictionary containing structured scorecard information.
    """
    if not isinstance(data, dict):
        raise ValueError("Scorecard data must be a dictionary.")

    raw_innings = data.get("scorecard", [])

    if not isinstance(raw_innings, list):
        raise ValueError("'scorecard' must contain a list of innings.")

    innings_list = []

    for inning in raw_innings:
        if not isinstance(inning, dict):
            continue

        fielding = []
        
        batting = []

        for player in inning.get("batsman", []):
            batting.append({
                "provider_player_id": player.get("id"),
                "player_name": player.get("name", "").strip(),
                "runs": _to_int(player.get("runs")),
                "balls_faced": _to_int(player.get("balls")),
                "fours": _to_int(player.get("fours")),
                "sixes": _to_int(player.get("sixes")),
                "strike_rate": _to_float(player.get("strkrate")),
                "dismissal": player.get("outdec", ""),
            })

            fielding_contribution = _parse_fielding_dismissal(
                player.get("outdec", "")
            )

            if fielding_contribution:
                fielding.append({
                    "provider_player_id": player.get("id"),
                    "dismissed_player_name": player.get("name", "").strip(),
                    **fielding_contribution,
                })

        bowling = []

        for player in inning.get("bowler", []):
            bowling.append({
                "provider_player_id": player.get("id"),
                "player_name": player.get("name", "").strip(),
                "legal_balls": _to_int(player.get("balls")),
                "maidens": _to_int(player.get("maidens")),
                "runs_conceded": _to_int(player.get("runs")),
                "wickets": _to_int(player.get("wickets")),
                "economy": _to_float(player.get("economy")),
            })

        partnerships = []

        partnership_data = inning.get("partnership") or {}
        raw_partnerships = partnership_data.get("partnership", [])

        for partnership in raw_partnerships:
            partnerships.append({
                "batter1_provider_id": partnership.get("bat1id"),
                "batter1_name": partnership.get("bat1name", "").strip(),
                "batter2_provider_id": partnership.get("bat2id"),
                "batter2_name": partnership.get("bat2name", "").strip(),
                "partnership_runs": _to_int(
                    partnership.get("totalruns")
                ),
                "partnership_balls": _to_int(
                    partnership.get("totalballs")
                ),
            })
        
        extras_data = inning.get("extras") or {}

        extras = {
            "byes": _to_int(extras_data.get("byes")),
            "legbyes": _to_int(extras_data.get("legbyes")),
            "wides": _to_int(extras_data.get("wides")),
            "noballs": _to_int(extras_data.get("noballs")),
            "penalty": _to_int(extras_data.get("penalty")),
            "total": _to_int(extras_data.get("total")),
        }

        innings_list.append({
            "innings_id": inning.get("inningsid"),
            "batting_team": inning.get("batteamname", ""),
            "team_score": _to_int(inning.get("score")),
            "wickets": _to_int(inning.get("wickets")),
            "overs": inning.get("overs"),
            "legal_balls": _to_int(inning.get("ballnbr")),
            "run_rate": _to_float(inning.get("runrate")),
            "is_declared": bool(inning.get("isdeclared", False)),
            "is_follow_on": bool(inning.get("isfollowon", False)),
            "extras": extras,
            "batting": batting,
            "bowling": bowling,
            "fielding": fielding,
            "partnerships": partnerships,
        })

    return {
        "match_status": data.get("status", ""),
        "is_match_complete": data.get("ismatchcomplete", False),
        "innings": innings_list,
    }
