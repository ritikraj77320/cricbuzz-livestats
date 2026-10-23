
from src.database.player_repository import (
    get_players,
    update_player,
    delete_player,
)

# Find the test player created in the previous step.
players = get_players(search="CRUD Test Player", limit=10)

if not players:
    print("Test player not found.")
else:
    player = players[0]
    player_id = player["player_id"]

    # Update the player's details.
    updated = update_player(
        player_id=player_id,
        player_name="CRUD Updated Player",
        role="All-rounder",
        date_of_birth="2002-05-15",
    )
    print("Updated:", updated)

    # Confirm the updated details.
    print("After update:", get_players(search="CRUD Updated Player"))

    # Delete only this test player.
    deleted = delete_player(player_id)
    print("Deleted:", deleted)

    # Confirm the player is gone.
    print("After delete:", get_players(search="CRUD Updated Player"))
