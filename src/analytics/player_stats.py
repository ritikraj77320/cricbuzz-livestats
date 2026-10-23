
"""SQL queries for match-specific cricket player statistics."""

import pandas as pd
from sqlalchemy import text

from src.database.connection import get_sqlalchemy_engine


def get_top_batters(
    limit: int = 10,
    match_id: int | None = None,
) -> pd.DataFrame:
    """Return batters ranked by runs in a selected match, or across matches."""

    match_filter = (
        "AND m.match_id = :match_id"
        if match_id is not None
        else ""
    )

    query = text(f"""
        SELECT
            p.player_name,
            t.team_name AS batting_team,
            SUM(bp.runs) AS total_runs,
            SUM(bp.balls_faced) AS balls_faced,
            SUM(bp.fours) AS fours,
            SUM(bp.sixes) AS sixes,
            ROUND(
                SUM(bp.runs)::numeric
                / NULLIF(SUM(bp.balls_faced), 0) * 100,
                2
            ) AS strike_rate
        FROM batting_performances AS bp
        JOIN players AS p
            ON p.player_id = bp.player_id
        JOIN innings AS i
            ON i.innings_id = bp.innings_id
        JOIN matches AS m
            ON m.match_id = i.match_id
        JOIN teams AS t
            ON t.team_id = i.batting_team_id
        WHERE NULLIF(TRIM(p.provider_player_id), '') IS NOT NULL
          AND NULLIF(TRIM(m.provider_match_id), '') IS NOT NULL
          {match_filter}
        GROUP BY p.player_id, p.player_name, t.team_name
        ORDER BY total_runs DESC, balls_faced ASC
        LIMIT :row_limit;
    """)

    params = {"row_limit": limit}
    if match_id is not None:
        params["match_id"] = match_id

    engine = get_sqlalchemy_engine()
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection, params=params)


def get_top_bowlers(
    limit: int = 10,
    match_id: int | None = None,
) -> pd.DataFrame:
    """Return bowlers ranked by wickets in a selected match, or across matches."""

    match_filter = (
        "AND m.match_id = :match_id"
        if match_id is not None
        else ""
    )

    query = text(f"""
        SELECT
            p.player_name,
            SUM(bp.wickets) AS total_wickets,
            SUM(bp.runs_conceded) AS runs_conceded,
            SUM(bp.legal_balls) AS legal_balls,
            (
                SUM(bp.legal_balls) / 6
            )::text || '.' ||
            (
                SUM(bp.legal_balls) % 6
            )::text AS overs,
            ROUND(
                SUM(bp.runs_conceded)::numeric
                / NULLIF(SUM(bp.legal_balls), 0) * 6,
                2
            ) AS economy
        FROM bowling_performances AS bp
        JOIN players AS p
            ON p.player_id = bp.player_id
        JOIN innings AS i
            ON i.innings_id = bp.innings_id
        JOIN matches AS m
            ON m.match_id = i.match_id
        WHERE NULLIF(TRIM(p.provider_player_id), '') IS NOT NULL
          AND NULLIF(TRIM(m.provider_match_id), '') IS NOT NULL
          {match_filter}
        GROUP BY p.player_id, p.player_name
        ORDER BY total_wickets DESC, economy ASC NULLS LAST
        LIMIT :row_limit;
    """)

    params = {"row_limit": limit}
    if match_id is not None:
        params["match_id"] = match_id

    engine = get_sqlalchemy_engine()
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection, params=params)
