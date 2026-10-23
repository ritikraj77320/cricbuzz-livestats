
from src.analytics.sql_analytics import (
    get_highest_team_scores,
    get_top_run_scorers,
    get_best_bowling_performances,
    get_match_status_summary,
)

print("\n1. HIGHEST TEAM SCORES")
print(get_highest_team_scores().to_string(index=False))

print("\n2. TOP RUN SCORERS")
print(get_top_run_scorers().to_string(index=False))

print("\n3. BEST BOWLING PERFORMANCES")
print(get_best_bowling_performances().to_string(index=False))

print("\n4. MATCH STATUS SUMMARY")
print(get_match_status_summary().to_string(index=False))
