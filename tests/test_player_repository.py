
from src.database.player_repository import (
    create_player,
    get_players,
)

# Create one test player.
player_id = create_player(
    player_name="CRUD Test Player",
    role="Batter",
    date_of_birth="2002-05-15",
)

print("Player created successfully.")
print("New player ID:", player_id)

# Read the newly created player.
players = get_players(search="CRUD Test Player")

print("\nRetrieved player:")
for player in players:
    print(player)
