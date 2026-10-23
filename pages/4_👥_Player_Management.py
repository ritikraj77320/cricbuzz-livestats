import pandas as pd
import streamlit as st
from src.database.player_repository import (
    create_player,
    get_players,
    update_player,
    delete_player,
)

st.set_page_config(
    page_title="Player Management | Cricbuzz LiveStats",
    page_icon="👥",
    layout="wide",
)

st.title("👥 Player Management")
st.caption("Create, search, update, and manage player records")
st.header("Player Management")

view_tab, add_tab, manage_tab = st.tabs(
    ["View Players", "Add Player", "Edit / Delete Player"]
)

# ---------- VIEW PLAYERS ----------
with view_tab:
    st.subheader("View and Search Players")

    search_name = st.text_input(
        "Search by player name",
        key="player_search_name",
    )

    if st.button("Search Players", key="search_players_button"):
        st.session_state["player_search_submitted"] = True

    # Show all players initially; apply search after submission.
    if (
        "player_search_submitted" not in st.session_state
        or not st.session_state["player_search_submitted"]
    ):
        players = get_players(limit=100)
    else:
        players = get_players(search=search_name, limit=100)

    if players:
        players_df = pd.DataFrame(players)

        # Display missing values more clearly.
        players_df = players_df.fillna("Not available")

        st.dataframe(
            players_df,
            hide_index=True,
            width="stretch",
        )
        st.caption(f"Showing {len(players)} player record(s).")
    else:
        st.info("No players found.")

# ---------- ADD PLAYER ----------
with add_tab:
    st.subheader("Add a New Player")

    with st.form("add_player_form", clear_on_submit=True):
        new_name = st.text_input("Player name")
        new_role = st.selectbox(
            "Role",
            ["Unknown", "Batter", "Bowler", "All-rounder", "Wicketkeeper"],
        )
        new_dob = st.date_input(
            "Date of birth",
            value=None,
            min_value=__import__("datetime").date(1900, 1, 1),
        )

        add_submitted = st.form_submit_button("Add Player")

    if add_submitted:
        if not new_name.strip():
            st.error("Please enter a player name.")
        else:
            try:
                player_id = create_player(
                    player_name=new_name,
                    role=None if new_role == "Unknown" else new_role,
                    date_of_birth=(
                        new_dob.isoformat() if new_dob else None
                    ),
                )
                st.success(
                    f"Player added successfully. Player ID: {player_id}"
                )
            except Exception as error:
                st.error(f"Could not add player: {error}")

# ---------- EDIT / DELETE PLAYER ----------
with manage_tab:
    st.subheader("Edit or Delete a Player")

    try:
        all_players = get_players(limit=1000)

        if not all_players:
            st.info("No player records are available.")
        else:
            player_options = {
                f"{p['player_name']} (ID: {p['player_id']})":
                p["player_id"]
                for p in all_players
            }

            selected_label = st.selectbox(
                "Select a player",
                list(player_options.keys()),
            )
            selected_id = player_options[selected_label]

            selected_player = next(
                p for p in all_players
                if p["player_id"] == selected_id
            )

            with st.form("edit_player_form"):
                edited_name = st.text_input(
                    "Player name",
                    value=selected_player["player_name"],
                )
                existing_role = selected_player["role"] or "Unknown"
                role_options = [
                    "Unknown",
                    "Batter",
                    "Bowler",
                    "All-rounder",
                    "Wicketkeeper",
                ]
                edited_role = st.selectbox(
                    "Role",
                    role_options,
                    index=(
                        role_options.index(existing_role)
                        if existing_role in role_options
                        else 0
                    ),
                )
                existing_dob = selected_player["date_of_birth"]
                edited_dob = st.date_input(
                    "Date of birth",
                    value=existing_dob,
                    min_value=__import__("datetime").date(1900, 1, 1),
                )
                update_submitted = st.form_submit_button(
                    "Save Changes"
                )

            if update_submitted:
                if not edited_name.strip():
                    st.error("Player name cannot be empty.")
                else:
                    try:
                        updated = update_player(
                            player_id=selected_id,
                            player_name=edited_name,
                            role=(
                                None
                                if edited_role == "Unknown"
                                else edited_role
                            ),
                            date_of_birth=(
                                edited_dob.isoformat()
                                if edited_dob
                                else None
                            ),
                        )
                        if updated:
                            st.success("Player updated successfully.")
                            st.rerun()
                        else:
                            st.warning("Player was not found.")
                    except Exception as error:
                        st.error(f"Could not update player: {error}")

            st.divider()
            st.warning(
                "Deleting a player may be blocked if cricket statistics "
                "refer to that player."
            )

            confirm_delete = st.checkbox(
                f"I confirm deletion of {selected_player['player_name']}",
                key=f"confirm_delete_{selected_id}",
            )

            if st.button(
                "Delete Selected Player",
                type="secondary",
                disabled=not confirm_delete,
            ):
                try:
                    deleted = delete_player(selected_id)
                    if deleted:
                        st.success("Player deleted successfully.")
                        st.rerun()
                    else:
                        st.warning("Player was not found.")
                except Exception:
                    st.error(
                        "Deletion failed. This player may be referenced "
                        "by batting, bowling, fielding, or partnership "
                        "records. Existing cricket statistics were "
                        "preserved."
                    )

    except Exception as error:
        st.error(f"Unable to load players: {error}")
