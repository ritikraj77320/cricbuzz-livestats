
import pandas as pd
from sqlalchemy import text
from src.database.connection import get_sqlalchemy_engine

query = text("""
    SELECT
        m.match_id,
        m.match_name,
        m.provider_match_id,
        COUNT(DISTINCT bp.bowling_performance_id) AS bowling_records,
        COUNT(DISTINCT bat.batting_performance_id) AS batting_records
    FROM matches AS m
    LEFT JOIN innings AS i
        ON i.match_id = m.match_id
    LEFT JOIN bowling_performances AS bp
        ON bp.innings_id = i.innings_id
    LEFT JOIN batting_performances AS bat
        ON bat.innings_id = i.innings_id
    WHERE m.provider_match_id IS NOT NULL
    GROUP BY
        m.match_id,
        m.match_name,
        m.provider_match_id
    ORDER BY bowling_records DESC;
""")

engine = get_sqlalchemy_engine()

with engine.connect() as connection:
    results = pd.read_sql_query(query, connection)

print(results.to_string(index=False))
