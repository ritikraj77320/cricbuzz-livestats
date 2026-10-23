
"""Read-only SQL query catalog for Cricbuzz LiveStats."""

import pandas as pd
from sqlalchemy import text

from src.database.connection import get_sqlalchemy_engine


QUERY_CATALOG = {
    "Match Analytics": {
        "01. All Matches": """
            SELECT match_id, match_name, match_format, status,
                   start_time, provider_match_id
            FROM matches
            ORDER BY start_time DESC NULLS LAST;
        """,
        "02. Matches by Format": """
            SELECT COALESCE(match_format, 'Unknown') AS match_format,
                   COUNT(*) AS match_count
            FROM matches
            GROUP BY match_format
            ORDER BY match_count DESC;
        """,
        "03. Matches by Status": """
            SELECT COALESCE(NULLIF(TRIM(status), ''), 'Unknown')
                       AS match_status,
                   COUNT(*) AS match_count
            FROM matches
            GROUP BY COALESCE(NULLIF(TRIM(status), ''), 'Unknown')
            ORDER BY match_count DESC;
        """,
        "04. Highest Scoring Innings": """
            SELECT m.match_name, t.team_name AS batting_team,
                   i.innings_number, i.total_runs, i.wickets,
                   i.legal_balls
            FROM innings i
            JOIN matches m ON m.match_id = i.match_id
            JOIN teams t ON t.team_id = i.batting_team_id
            ORDER BY i.total_runs DESC NULLS LAST
            LIMIT :row_limit;
        """,
        "05. Matches by Series": """
            SELECT COALESCE(s.series_name, 'Unassigned') AS series_name,
                   COUNT(m.match_id) AS match_count
            FROM series s
            LEFT JOIN matches m ON m.series_id = s.series_id
            GROUP BY s.series_id, s.series_name
            ORDER BY match_count DESC;
        """,
        "06. Matches by Venue": """
            SELECT v.venue_name, v.city, v.country,
                   COUNT(m.match_id) AS match_count
            FROM venues v
            LEFT JOIN matches m ON m.venue_id = v.venue_id
            GROUP BY v.venue_id, v.venue_name, v.city, v.country
            ORDER BY match_count DESC;
        """,
    },

    "Batting Analytics": {
        "07. Top Run Scorers": """
            SELECT p.player_name, SUM(bp.runs) AS total_runs,
                   COUNT(DISTINCT i.match_id) AS matches_played
            FROM batting_performances bp
            JOIN players p ON p.player_id = bp.player_id
            JOIN innings i ON i.innings_id = bp.innings_id
            GROUP BY p.player_id, p.player_name
            ORDER BY total_runs DESC
            LIMIT :row_limit;
        """,
        "08. Highest Individual Scores": """
            SELECT p.player_name, m.match_name, i.innings_number,
                   bp.runs, bp.balls_faced, bp.fours, bp.sixes
            FROM batting_performances bp
            JOIN players p ON p.player_id = bp.player_id
            JOIN innings i ON i.innings_id = bp.innings_id
            JOIN matches m ON m.match_id = i.match_id
            ORDER BY bp.runs DESC
            LIMIT :row_limit;
        """,
        "09. Most Fours": """
            SELECT p.player_name, SUM(bp.fours) AS total_fours
            FROM batting_performances bp
            JOIN players p ON p.player_id = bp.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY total_fours DESC
            LIMIT :row_limit;
        """,
        "10. Most Sixes": """
            SELECT p.player_name, SUM(bp.sixes) AS total_sixes
            FROM batting_performances bp
            JOIN players p ON p.player_id = bp.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY total_sixes DESC
            LIMIT :row_limit;
        """,
        "11. Highest Strike Rates": """
            SELECT p.player_name, SUM(bp.runs) AS total_runs,
                   SUM(bp.balls_faced) AS total_balls,
                   ROUND(
                       SUM(bp.runs)::numeric * 100
                       / NULLIF(SUM(bp.balls_faced), 0), 2
                   ) AS strike_rate
            FROM batting_performances bp
            JOIN players p ON p.player_id = bp.player_id
            GROUP BY p.player_id, p.player_name
            HAVING SUM(bp.balls_faced) > 0
            ORDER BY strike_rate DESC
            LIMIT :row_limit;
        """,
        "12. Batting Contributions by Team": """
            SELECT t.team_name, SUM(bp.runs) AS total_runs,
                   COUNT(*) AS batting_innings,
                   ROUND(AVG(bp.runs)::numeric, 2) AS average_runs
            FROM batting_performances bp
            JOIN innings i ON i.innings_id = bp.innings_id
            JOIN teams t ON t.team_id = i.batting_team_id
            GROUP BY t.team_id, t.team_name
            ORDER BY total_runs DESC;
        """,
        "13. Players with Most Batting Innings": """
            SELECT p.player_name, COUNT(*) AS innings_batted,
                   SUM(bp.runs) AS total_runs
            FROM batting_performances bp
            JOIN players p ON p.player_id = bp.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY innings_batted DESC, total_runs DESC
            LIMIT :row_limit;
        """,
    },

    "Bowling Analytics": {
        "14. Top Wicket Takers": """
            SELECT p.player_name, SUM(bp.wickets) AS total_wickets,
                   SUM(bp.runs_conceded) AS runs_conceded,
                   SUM(bp.legal_balls) AS legal_balls
            FROM bowling_performances bp
            JOIN players p ON p.player_id = bp.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY total_wickets DESC, runs_conceded ASC
            LIMIT :row_limit;
        """,
        "15. Best Bowling Innings": """
            SELECT p.player_name, m.match_name, i.innings_number,
                   bp.wickets, bp.runs_conceded, bp.legal_balls,
                   bp.economy
            FROM bowling_performances bp
            JOIN players p ON p.player_id = bp.player_id
            JOIN innings i ON i.innings_id = bp.innings_id
            JOIN matches m ON m.match_id = i.match_id
            ORDER BY bp.wickets DESC, bp.runs_conceded ASC
            LIMIT :row_limit;
        """,
        "16. Lowest Economy Rates": """
            SELECT p.player_name, SUM(bp.runs_conceded) AS runs_conceded,
                   SUM(bp.legal_balls) AS legal_balls,
                   ROUND(
                       SUM(bp.runs_conceded)::numeric * 6
                       / NULLIF(SUM(bp.legal_balls), 0), 2
                   ) AS economy
            FROM bowling_performances bp
            JOIN players p ON p.player_id = bp.player_id
            GROUP BY p.player_id, p.player_name
            HAVING SUM(bp.legal_balls) > 0
            ORDER BY economy ASC
            LIMIT :row_limit;
        """,
        "17. Most Maiden Overs": """
            SELECT p.player_name, SUM(bp.maidens) AS total_maidens
            FROM bowling_performances bp
            JOIN players p ON p.player_id = bp.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY total_maidens DESC
            LIMIT :row_limit;
        """,
        "18. Bowling Workload": """
            SELECT p.player_name,
                   SUM(bp.legal_balls) AS legal_balls,
                   ROUND(SUM(bp.legal_balls)::numeric / 6, 2)
                       AS overs_decimal,
                   SUM(bp.runs_conceded) AS runs_conceded,
                   SUM(bp.wickets) AS wickets
            FROM bowling_performances bp
            JOIN players p ON p.player_id = bp.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY legal_balls DESC
            LIMIT :row_limit;
        """,
        "19. Bowling Figures by Match": """
            SELECT p.player_name, m.match_name, i.innings_number,
                   bp.wickets, bp.runs_conceded, bp.economy
            FROM bowling_performances bp
            JOIN players p ON p.player_id = bp.player_id
            JOIN innings i ON i.innings_id = bp.innings_id
            JOIN matches m ON m.match_id = i.match_id
            ORDER BY m.start_time DESC NULLS LAST,
                     bp.wickets DESC;
        """,
    },

    "Player Analytics": {
        "20. Player Directory": """
            SELECT player_id, player_name, role, date_of_birth
            FROM players
            ORDER BY player_name;
        """,
        "21. Players by Role": """
            SELECT COALESCE(NULLIF(TRIM(role), ''), 'Unknown') AS role,
                   COUNT(*) AS player_count
            FROM players
            GROUP BY COALESCE(NULLIF(TRIM(role), ''), 'Unknown')
            ORDER BY player_count DESC;
        """,
        "22. All-Rounder Contributions": """
            WITH batting AS (
                SELECT player_id, SUM(runs) AS runs
                FROM batting_performances
                GROUP BY player_id
            ),
            bowling AS (
                SELECT player_id, SUM(wickets) AS wickets
                FROM bowling_performances
                GROUP BY player_id
            )
            SELECT p.player_name,
                   COALESCE(b.runs, 0) AS runs,
                   COALESCE(w.wickets, 0) AS wickets
            FROM players p
            JOIN batting b ON b.player_id = p.player_id
            JOIN bowling w ON w.player_id = p.player_id
            ORDER BY runs DESC, wickets DESC
            LIMIT :row_limit;
        """,
        "23. Player Match Appearances": """
            WITH appearances AS (
                SELECT bp.player_id, i.match_id
                FROM batting_performances bp
                JOIN innings i ON i.innings_id = bp.innings_id
                UNION
                SELECT bp.player_id, i.match_id
                FROM bowling_performances bp
                JOIN innings i ON i.innings_id = bp.innings_id
                UNION
                SELECT fp.player_id, i.match_id
                FROM fielding_performances fp
                JOIN innings i ON i.innings_id = fp.innings_id
            )
            SELECT p.player_name, COUNT(*) AS matches_with_records
            FROM appearances a
            JOIN players p ON p.player_id = a.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY matches_with_records DESC
            LIMIT :row_limit;
        """,
    },

    "Team Analytics": {
        "24. Team Directory": """
            SELECT team_id, team_name, country
            FROM teams
            ORDER BY team_name;
        """,
        "25. Team Match Participation": """
            SELECT t.team_name, COUNT(*) AS match_participations
            FROM matches m
            JOIN teams t ON t.team_id = m.team1_id
            GROUP BY t.team_id, t.team_name
            UNION ALL
            SELECT t.team_name, COUNT(*) AS match_participations
            FROM matches m
            JOIN teams t ON t.team_id = m.team2_id
            GROUP BY t.team_id, t.team_name
            ORDER BY match_participations DESC;
        """,
        "26. Average Innings Score by Team": """
            SELECT t.team_name, COUNT(*) AS innings_count,
                   ROUND(AVG(i.total_runs)::numeric, 2) AS average_score,
                   MAX(i.total_runs) AS highest_score
            FROM innings i
            JOIN teams t ON t.team_id = i.batting_team_id
            GROUP BY t.team_id, t.team_name
            ORDER BY average_score DESC;
        """,
    },

    "Fielding & Partnerships": {
        "27. Most Catches": """
            SELECT p.player_name, SUM(fp.catches) AS catches
            FROM fielding_performances fp
            JOIN players p ON p.player_id = fp.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY catches DESC
            LIMIT :row_limit;
        """,
        "28. Most Run Outs": """
            SELECT p.player_name, SUM(fp.run_outs) AS run_outs
            FROM fielding_performances fp
            JOIN players p ON p.player_id = fp.player_id
            GROUP BY p.player_id, p.player_name
            ORDER BY run_outs DESC
            LIMIT :row_limit;
        """,
        "29. Highest Partnerships": """
            SELECT m.match_name, i.innings_number,
                   p1.player_name AS batter1,
                   p2.player_name AS batter2,
                   bp.partnership_runs, bp.partnership_balls
            FROM batting_partnerships bp
            JOIN innings i ON i.innings_id = bp.innings_id
            JOIN matches m ON m.match_id = i.match_id
            JOIN players p1 ON p1.player_id = bp.batter1_id
            JOIN players p2 ON p2.player_id = bp.batter2_id
            ORDER BY bp.partnership_runs DESC
            LIMIT :row_limit;
        """,
    },

    "Advanced SQL": {
        "30. Ranked Batting Scores": """
            WITH player_scores AS (
                SELECT p.player_id, p.player_name,
                       SUM(bp.runs) AS total_runs
                FROM batting_performances bp
                JOIN players p ON p.player_id = bp.player_id
                GROUP BY p.player_id, p.player_name
            )
            SELECT player_name, total_runs,
                   DENSE_RANK() OVER (ORDER BY total_runs DESC) AS rank
            FROM player_scores
            ORDER BY rank, player_name
            LIMIT :row_limit;
        """,
        "31. Innings Above Match Average": """
            WITH match_average AS (
                SELECT match_id, AVG(total_runs) AS average_runs
                FROM innings
                GROUP BY match_id
            )
            SELECT m.match_name, t.team_name AS batting_team,
                   i.innings_number, i.total_runs,
                   ROUND(a.average_runs::numeric, 2) AS match_average
            FROM innings i
            JOIN matches m ON m.match_id = i.match_id
            JOIN teams t ON t.team_id = i.batting_team_id
            JOIN match_average a ON a.match_id = i.match_id
            WHERE i.total_runs > a.average_runs
            ORDER BY i.total_runs DESC;
        """,
        "32. Cumulative Runs by Batter": """
            SELECT p.player_name, i.match_id, m.match_name,
                   bp.runs,
                   SUM(bp.runs) OVER (
                       PARTITION BY p.player_id
                       ORDER BY m.start_time NULLS FIRST, i.innings_id,
                                bp.batting_performance_id
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                   ) AS cumulative_recorded_runs
            FROM batting_performances bp
            JOIN players p ON p.player_id = bp.player_id
            JOIN innings i ON i.innings_id = bp.innings_id
            JOIN matches m ON m.match_id = i.match_id
            ORDER BY p.player_name, m.start_time NULLS FIRST;
        """,
    },
}


def get_query_catalog() -> dict:
    """Return the predefined analytics query catalog."""
    return QUERY_CATALOG


def run_analytics_query(
    category: str,
    query_name: str,
    limit: int = 100,
) -> pd.DataFrame:
    """Execute one approved, read-only analytics query."""
    if category not in QUERY_CATALOG:
        raise ValueError("Unknown analytics category.")

    if query_name not in QUERY_CATALOG[category]:
        raise ValueError("Unknown analytics query.")

    if not 1 <= limit <= 1000:
        raise ValueError("Result limit must be between 1 and 1000.")

    sql = QUERY_CATALOG[category][query_name].strip().rstrip(";")

    # Queries with a limit parameter use the user-selected row limit.
    # Other catalog queries run as written.
    parameters = {}
    if ":row_limit" in sql:
        parameters["row_limit"] = limit

    # Only execute the fixed, application-defined query catalog.
    if not sql.upper().startswith(("SELECT", "WITH")):
        raise ValueError("Only read-only SELECT queries are allowed.")

    engine = get_sqlalchemy_engine()

    with engine.connect() as connection:
        return pd.read_sql_query(
            text(sql),
            connection,
            params=parameters,
        )


# Backward-compatible functions for the existing Streamlit page.


def get_highest_team_scores(limit: int = 10) -> pd.DataFrame:
    return run_analytics_query(
        "Match Analytics", "04. Highest Scoring Innings", limit
    )


def get_top_run_scorers(limit: int = 10) -> pd.DataFrame:
    return run_analytics_query(
        "Batting Analytics", "07. Top Run Scorers", limit
    )


def get_best_bowling_performances(limit: int = 10) -> pd.DataFrame:
    return run_analytics_query(
        "Bowling Analytics", "15. Best Bowling Innings", limit
    )


def get_match_status_summary() -> pd.DataFrame:
    return run_analytics_query("Match Analytics", "03. Matches by Status")
