
import pandas as pd
import streamlit as st

from src.database.connection import get_sqlalchemy_engine
from src.api.api_client import get_match_scorecard
from src.api.scorecard_parser import parse_scorecard


st.set_page_config(
    page_title="Player Statistics | Cricbuzz LiveStats",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Player Statistics")
st.caption("Top batters and bowlers from the selected match")


@st.cache_resource
def get_engine():
    return get_sqlalchemy_engine()


@st.cache_data(ttl=30)
def load_matches():
    query = """
        SELECT
            m.match_id,
            m.match_name,
            m.match_format,
            m.provider_match_id,
            t1.team_name AS team1,
            t2.team_name AS team2
        FROM matches m
        JOIN teams t1 ON t1.team_id = m.team1_id
        JOIN teams t2 ON t2.team_id = m.team2_id
        WHERE NULLIF(TRIM(m.provider_match_id), '') IS NOT NULL
        ORDER BY m.start_time DESC NULLS LAST;
    """

    with get_engine().connect() as connection:
        return pd.read_sql_query(query, connection)


@st.cache_data(ttl=30)
def load_scorecard(provider_match_id):
    raw_data = get_match_scorecard(str(provider_match_id))
    return parse_scorecard(raw_data)


try:
    matches_df = load_matches()

    if matches_df.empty:
        st.warning("No matches found. Please sync matches first.")
        st.stop()

    matches_df["display_name"] = (
        matches_df["team1"].fillna("Unknown")
        + " vs "
        + matches_df["team2"].fillna("Unknown")
        + " | "
        + matches_df["match_format"].fillna("Unknown format")
    )

    selected_label = st.selectbox(
        "Select a match",
        matches_df["display_name"].tolist(),
    )

    selected_match = matches_df[
        matches_df["display_name"] == selected_label
    ].iloc[0]

    if st.button("Refresh statistics"):
        load_scorecard.clear()
        st.rerun()

    scorecard = load_scorecard(
        str(selected_match["provider_match_id"])
    )

    innings_list = scorecard.get("innings", [])

    if not innings_list:
        st.info("No player statistics are available for this match.")
        st.stop()

    # Combine player performances across all innings.
    batter_stats = {}
    bowler_stats = {}

    for inning in innings_list:

        for batter in inning.get("batting", []):
            name = batter.get("player_name") or "Unknown"

            if name not in batter_stats:
                batter_stats[name] = {
                    "Player": name,
                    "Runs": 0,
                    "Balls": 0,
                    "4s": 0,
                    "6s": 0,
                }

            stats = batter_stats[name]
            stats["Runs"] += int(batter.get("runs") or 0)
            stats["Balls"] += int(batter.get("balls_faced") or 0)
            stats["4s"] += int(batter.get("fours") or 0)
            stats["6s"] += int(batter.get("sixes") or 0)

        for bowler in inning.get("bowling", []):
            name = bowler.get("player_name") or "Unknown"

            if name not in bowler_stats:
                bowler_stats[name] = {
                    "Player": name,
                    "Balls": 0,
                    "Runs Conceded": 0,
                    "Wickets": 0,
                }

            stats = bowler_stats[name]
            stats["Balls"] += int(bowler.get("legal_balls") or 0)
            stats["Runs Conceded"] += int(
                bowler.get("runs_conceded") or 0
            )
            stats["Wickets"] += int(bowler.get("wickets") or 0)

    # Build the Top Batters table.
    batters_df = pd.DataFrame(list(batter_stats.values()))

    if not batters_df.empty:
        batters_df["Strike Rate"] = (
            batters_df["Runs"]
            .div(batters_df["Balls"].replace(0, float("nan")))
            .mul(100)
            .round(2)
)
        batters_df = batters_df.sort_values(
            ["Runs", "Strike Rate"],
            ascending=[False, False],
        ).head(10)

    # Build the Top Bowlers table.
    bowlers_df = pd.DataFrame(list(bowler_stats.values()))

    if not bowlers_df.empty:
        bowlers_df["Overs"] = bowlers_df["Balls"].apply(
            lambda balls: f"{balls // 6}.{balls % 6}"
        )

        bowlers_df["Economy"] = (
            bowlers_df["Runs Conceded"]
            .mul(6)
            .div(bowlers_df["Balls"].replace(0, float("nan")))
            .round(2)
        )

        bowlers_df = bowlers_df.sort_values(
            ["Wickets", "Economy"],
            ascending=[False, True],
        ).head(10)

    # Top Performer Highlights
    st.subheader("🌟 Match Top Performers")

    top_batter = None
    top_bowler = None

    if not batters_df.empty:
        top_batter = batters_df.sort_values(
            ["Runs", "Strike Rate"],
            ascending=[False, False],
            na_position="last",
        ).iloc[0]

    if not bowlers_df.empty:
        top_bowler = bowlers_df.sort_values(
            ["Wickets", "Economy"],
            ascending=[False, True],
            na_position="last",
        ).iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        if top_batter is not None:
            st.metric(
                label="🏏 Top Batter",
                value=str(top_batter["Player"]),
                delta=f'{int(top_batter["Runs"])} runs',
            )
            st.caption(
                f'{int(top_batter["Balls"])} balls faced | '
                f'Strike rate: {top_batter["Strike Rate"]}'
            )
        else:
            st.info("No batting performer available.")

    with col2:
        if top_bowler is not None:
            st.metric(
                label="🎯 Top Bowler",
                value=str(top_bowler["Player"]),
                delta=f'{int(top_bowler["Wickets"])} wickets',
            )
            st.caption(
                f'{top_bowler["Overs"]} overs | '
                f'{int(top_bowler["Runs Conceded"])} runs conceded | '
                f'Economy: {top_bowler["Economy"]}'
            )
        else:
            st.info("No bowling performer available.")

    st.subheader("🏏 Top Batters")

    if batters_df.empty:
        st.info("No batting statistics available.")
    else:
        st.dataframe(
            batters_df[
                ["Player", "Runs", "Balls", "4s", "6s", "Strike Rate"]
            ],
            hide_index=True,
            width="stretch",
        )

    st.subheader("🎯 Top Bowlers")

    if bowlers_df.empty:
        st.info("No bowling statistics available.")
    else:
        st.dataframe(
            bowlers_df[
                [
                    "Player",
                    "Overs",
                    "Runs Conceded",
                    "Wickets",
                    "Economy",
                ]
            ],
            hide_index=True,
            width="stretch",
        )

except Exception as error:
    st.error("Unable to load player statistics.")
    st.caption(f"{type(error).__name__}: {error}")
