
"""Home page for Cricbuzz LiveStats."""

import streamlit as st

st.set_page_config(
    page_title="Cricbuzz LiveStats | Home",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- HERO SECTION ----------
st.title("🏏 Cricbuzz LiveStats")
st.subheader("Cricket insights powered by Cricbuzz and PostgreSQL")

st.markdown(
    """
    Welcome to **Cricbuzz LiveStats**, a cricket analytics application
    built with Python, Streamlit, PostgreSQL, and the Cricbuzz API.

    Explore match information, analyze player performances, run SQL
    analytics, and manage player records through an interactive interface.
    """
)

st.divider()

# ---------- QUICK NAVIGATION ----------
st.header("Explore the Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏏 Live Match")
    st.write(
        "Explore match records, current match status, and available "
        "scorecard information."
    )
    st.page_link(
        "pages/1_🏏_Live_Matches.py",
        label="Open Live Matches",
        icon="🏏",
        use_container_width=True,
    )

    st.subheader("📊 SQL Queries & Analytics")
    st.write(
        "Explore SQL query results, batting and bowling analysis, "
        "innings totals, and match-status summaries."
    )
    st.page_link(
        "pages/3_📊_SQL_Analytics.py",
        label="Open SQL Analytics",
        icon="📊",
        use_container_width=True,
    )

with col2:
    st.subheader("🏆 Top Player Stats")
    st.write(
        "Compare top batters, run scorers, wicket takers, and "
        "other available player statistics."
    )
    st.page_link(
        "pages/2_🏆_Player_Statistics.py",
        label="Open Player Statistics",
        icon="🏆",
        use_container_width=True,
    )

    st.subheader("👥 CRUD Operations")
    st.write(
        "View, search, create, update, and delete player records "
        "subject to database constraints."
    )
    st.page_link(
        "pages/4_👥_Player_Management.py",
        label="Open Player Management",
        icon="👥",
        use_container_width=True,
    )

st.divider()

# ---------- PROJECT OVERVIEW ----------
st.header("About the Project")

st.write(
    """
    Cricbuzz LiveStats demonstrates how an API-driven application can
    collect cricket data, store structured records in a relational
    database, and present useful statistics through a web dashboard.
    """
)

st.subheader("Technology Stack")

st.markdown(
    """
    - **Python:** application logic and data processing
    - **Streamlit:** interactive web interface
    - **PostgreSQL:** relational data storage
    - **Pandas:** tabular data processing
    - **SQLAlchemy and Psycopg:** database connectivity and queries
    - **Requests:** API communication
    - **python-dotenv:** local environment configuration
    """
)

st.subheader("Main Project Features")

st.markdown(
    """
    - Live-match data synchronization
    - Match and scorecard data processing
    - Top batting and bowling statistics
    - SQL-based cricket analytics
    - Player record management using CRUD operations
    """
)

st.divider()

# ---------- GETTING STARTED ----------
st.header("Getting Started")

st.markdown(
    """
    1. Configure PostgreSQL and create the project database.
    2. Set your API and database credentials in a local `.env` file.
    3. Install dependencies from `requirements.txt`.
    4. Start the application using `streamlit run app.py`.
    5. Use the sidebar or navigation links above to explore each page.
    """
)

st.info(
    "API availability and the completeness of match and player statistics "
    "depend on the configured provider and the data imported into PostgreSQL."
)

st.subheader("Project Documentation")

st.write(
    "See the project's README.md for the installation guide, "
    "configuration, database setup, project structure, and testing steps."
)

st.caption(
    "Cricbuzz LiveStats — Educational cricket analytics project."
)
