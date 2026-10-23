import pandas as pd
import streamlit as st
import subprocess
import sys

from src.database.connection import get_sqlalchemy_engine
from src.api.api_client import get_match_scorecard
from src.api.scorecard_parser import parse_scorecard

@st.cache_resource
def get_cached_engine():
    return get_sqlalchemy_engine()


@st.cache_data(ttl=30)
def load_matches():
    """Load match records from PostgreSQL."""
    query = """
        SELECT
            m.match_id,
            m.match_name,
            t1.team_name AS team1,
            t2.team_name AS team2,
            m.match_format,
            m.start_time,
            m.status,
            s.series_name,
            v.venue_name
        FROM matches AS m
        JOIN teams AS t1 ON m.team1_id = t1.team_id
        JOIN teams AS t2 ON m.team2_id = t2.team_id
        LEFT JOIN series AS s ON m.series_id = s.series_id
        LEFT JOIN venues AS v ON m.venue_id = v.venue_id
        ORDER BY m.start_time DESC NULLS LAST
    """
    engine = get_cached_engine()
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection)


st.set_page_config(
    page_title="Cricbuzz LiveStats | Live Matches",
    page_icon="🏏",
    layout="wide",
)

st.title("🏏 Cricbuzz LiveStats")
st.caption("Cricket insights powered by Cricbuzz and PostgreSQL")


# Add these imports at the top of app.py, with your other imports.

if st.button("Sync latest Cricbuzz data", type="primary"):
    with st.spinner("Fetching API data and updating PostgreSQL..."):
        try:
            subprocess.run(
                [sys.executable, "-m", "src.sync_pipeline"],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            load_matches.clear()
            st.success("Cricbuzz data synced successfully!")
            st.rerun()

        except subprocess.CalledProcessError as error:
            st.error("The sync pipeline failed.")
            st.code(error.stderr or error.stdout or str(error))

        except subprocess.TimeoutExpired:
            st.error(
                "The sync took longer than 120 seconds. "
                "Check the terminal and try again later."
            )


try:
    matches_df = load_matches()
    # Display match start times in Indian Standard Time.
    matches_df["start_time"] = pd.to_datetime(
        matches_df["start_time"], utc=True
    ).dt.tz_convert("Asia/Kolkata")
except Exception as error:
    st.error("Could not load matches from PostgreSQL.")
    st.caption(f"Error type: {type(error).__name__}")
    st.info(
        "Check your PostgreSQL service and the database settings in .env."
    )

if matches_df.empty:
    st.info("No match records found. Run the sync pipeline first.")

status = matches_df["status"].fillna("").str.strip().str.lower()

completed = int(status.isin(["complete", "completed", "won"]).sum())
scheduled = int(status.isin(["scheduled", "upcoming"]).sum())

active_statuses = [
    "in progress",
    "innings break",
    "lunch",
    "stumps",
]
active = int(status.isin(active_statuses).sum())

col1, col2, col3, col4 = st.columns(4)

col1.metric("Matches in database", len(matches_df), border=True)
col2.metric("Active matches", active, border=True)
col3.metric("Completed matches", completed, border=True)
col4.metric("Scheduled matches", scheduled, border=True)

st.subheader("🔴 Live Matches")

active_statuses = [
    "in progress",
    "live",
    "innings break",
    "lunch",
    "tea",
    "stumps",
    "drinks break",
    "strategic timeout",
]

status = matches_df["status"].fillna("").str.strip().str.lower()

live_matches = matches_df[
    status.isin(active_statuses)
].copy()

if live_matches.empty:
    st.info(
        "No matches currently have an active-play status from the API."
    )
else:
    st.caption(f"{len(live_matches)} active match(es) found")

    for _, match in live_matches.iterrows():
        team1 = match["team1"] or "Team 1"
        team2 = match["team2"] or "Team 2"
        match_format = match["match_format"] or "Format unavailable"
        match_status = match["status"] or "Status unavailable"
        series_name = match["series_name"] or "Series unavailable"
        venue = match["venue_name"] or "Venue unavailable"

        with st.container(border=True):
            left, right = st.columns([3, 1])

            with left:
                st.markdown(f"### 🏏 {team1} vs {team2}")
                st.caption(f"{series_name} · {venue}")

            with right:
                st.markdown(f"**{match_format}**")
                st.markdown(f"🔴 **{match_status}**")

            st.caption(
                "Detailed scores are available in the scorecard section below."
            )


st.subheader("All Match Records")

search = st.text_input(
    "Search by team, series, or venue",
    placeholder="e.g. Zimbabwe, ODI, UAE...",
)

available_statuses = sorted(
    matches_df["status"].dropna().unique().tolist()
)

selected_statuses = st.multiselect(
    "Filter by status",
    options=available_statuses,
    default=available_statuses,
)

filtered_df = matches_df[
    matches_df["status"].isin(selected_statuses)
].copy()

if search.strip():
    searchable = (
        filtered_df[
            [
                "match_name",
                "team1",
                "team2",
                "series_name",
                "venue_name",
                "match_format",
                "status",
            ]
        ]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    )
    filtered_df = filtered_df[
        searchable.str.contains(search.strip(), case=False, regex=False)
    ]

display_df = filtered_df.rename(
    columns={
        "match_name": "Match",
        "team1": "Team 1",
        "team2": "Team 2",
        "match_format": "Format",
        "start_time": "Start Time",
        "status": "Status",
        "series_name": "Series",
        "venue_name": "Venue",
    }
)

st.dataframe(
display_df[["Match", "Team 1", "Team 2", "Format",
            "Start Time", "Status", "Series", "Venue"]],
width="stretch",
hide_index=True,
)

st.caption(
    f"Showing {len(filtered_df)} of {len(matches_df)} database records. "
    "Match status is provided by the API and may not represent a live match."
)


@st.cache_data(ttl=30)
def load_scorecard_matches():
    """Load match records with Cricbuzz provider IDs."""
    query = """
        SELECT
            m.provider_match_id,
            m.match_name,
            t1.team_name AS team1,
            t2.team_name AS team2,
            m.match_format,
            m.status,
            m.start_time,
            v.venue_name,
            v.city
        FROM matches AS m
        JOIN teams AS t1 ON t1.team_id = m.team1_id
        JOIN teams AS t2 ON t2.team_id = m.team2_id
        LEFT JOIN venues AS v ON v.venue_id = m.venue_id
        WHERE m.provider_match_id IS NOT NULL
          AND TRIM(m.provider_match_id) <> ''
        ORDER BY m.start_time DESC NULLS LAST;
    """

    engine = get_cached_engine()
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection)


@st.cache_data(ttl=30)
def load_parsed_scorecard(provider_match_id):
    """Fetch and parse a scorecard from Cricbuzz."""
    raw_scorecard = get_match_scorecard(provider_match_id)
    return parse_scorecard(raw_scorecard)


# ---------------- MATCH SCORECARD ----------------

st.divider()
st.header("Detailed Match Scorecard")

try:
    scorecard_matches = load_scorecard_matches()

    if scorecard_matches.empty:
        st.info(
            "No matches with Cricbuzz provider IDs are available."
        )
    else:
        scorecard_matches["display_name"] = (
            scorecard_matches["team1"].fillna("Unknown")
            + " vs "
            + scorecard_matches["team2"].fillna("Unknown")
            + " | "
            + scorecard_matches["match_name"].fillna("Match")
            + " | ID: "
            + scorecard_matches["provider_match_id"].astype(str)
        )

        selected_match_label = st.selectbox(
            "Select a match to view its scorecard",
            scorecard_matches["display_name"].tolist(),
            key="scorecard_match_selector",
        )

        selected_match = scorecard_matches.loc[
            scorecard_matches["display_name"] == selected_match_label
        ].iloc[0]

        info_col1, info_col2, info_col3 = st.columns(3)

        info_col1.metric(
            "Format",
            selected_match["match_format"] or "Unknown",
        )
        info_col2.metric(
            "Status",
            selected_match["status"] or "Unknown",
        )
        info_col3.metric(
            "Venue",
            selected_match["venue_name"] or "Not available",
        )

        if selected_match["city"]:
            st.caption(f"City: {selected_match['city']}")

        if st.button("Refresh selected scorecard"):
            load_parsed_scorecard.clear()
            st.rerun()

        try:
            scorecard = load_parsed_scorecard(
                str(selected_match["provider_match_id"])
            )

            st.subheader("Match Status")
            st.write(scorecard.get("match_status") or "Not available")

            innings_list = scorecard.get("innings", [])

            if not innings_list:
                st.info(
                    "The API returned no innings for this match."
                )

            for inning in innings_list:
                batting_team = inning.get(
                    "batting_team", "Unknown team"
                )

                st.subheader(
                    f"Innings {inning.get('innings_id', '')}: "
                    f"{batting_team}"
                )

                total_runs = inning.get("team_score", 0)
                wickets = inning.get("wickets", 0)
                legal_balls = inning.get("legal_balls", 0)
                overs = f"{legal_balls // 6}.{legal_balls % 6}"

                st.markdown(
                    f"### {total_runs}/{wickets} "
                    f"({overs} overs)"
                )

                batting = inning.get("batting", [])
                if batting:
                    st.markdown("**Batting scorecard**")
                    st.dataframe(
                        pd.DataFrame(batting),
                        hide_index=True,
                        width="stretch",
                    )

                bowling = inning.get("bowling", [])
                if bowling:
                    st.markdown("**Bowling scorecard**")
                    st.dataframe(
                        pd.DataFrame(bowling),
                        hide_index=True,
                        width="stretch",
                    )

        except Exception as error:
            st.warning(
                "Unable to load this match's scorecard. "
                "The selected match may not have scorecard data, "
                "or the API request may have failed."
            )
            st.caption(str(error))

except Exception as error:
    st.error("Unable to load matches for the scorecard selector.")
    st.caption(str(error))


