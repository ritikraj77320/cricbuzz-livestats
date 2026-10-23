
from src.analytics.player_stats import (
    get_top_batters,
    get_top_bowlers,
)

print("\nTOP BATTERS")
print(get_top_batters().to_string(index=False))

print("\nTOP BOWLERS")
print(get_top_bowlers().to_string(index=False))
