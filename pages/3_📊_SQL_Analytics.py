
import streamlit as st

from src.analytics.sql_analytics import (
    get_query_catalog,
    run_analytics_query,
)

st.set_page_config(
    page_title="SQL Analytics | Cricbuzz LiveStats",
    page_icon="📊",
    layout="wide",
)

st.title("📊 SQL Queries & Analytics")
st.caption(
    "Explore cricket data using 32 predefined PostgreSQL analytics queries."
)

catalog = get_query_catalog()
total_queries = sum(len(queries) for queries in catalog.values())

col1, col2 = st.columns(2)
col1.metric("Available SQL Queries", total_queries)
col2.metric("Query Categories", len(catalog))

st.divider()

category = st.selectbox(
    "Select a query category",
    list(catalog.keys()),
)

query_names = list(catalog[category].keys())

query_name = st.selectbox(
    "Select an SQL query",
    query_names,
)

st.caption(f"Category: {category} · Query: {query_name}")

limit = st.slider(
    "Maximum result rows (where applicable)",
    min_value=5,
    max_value=100,
    value=10,
    step=5,
)

with st.expander("About this query"):
    st.write(
        "This query is predefined by the application and runs against "
        "your PostgreSQL database. Queries are read-only."
    )

if st.button("▶ Run SQL Query", type="primary"):
    try:
        with st.spinner("Executing SQL query..."):
            results_df = run_analytics_query(
                category,
                query_name,
                limit,
            )

        st.session_state["sql_analytics_results"] = results_df
        st.session_state["sql_analytics_query"] = query_name

    except Exception as error:
        st.error("Unable to execute the selected query.")
        st.exception(error)

if "sql_analytics_results" in st.session_state:
    results_df = st.session_state["sql_analytics_results"]
    previous_query = st.session_state.get(
        "sql_analytics_query",
        "",
    )

    if previous_query:
        st.subheader(f"Results: {previous_query}")

    st.metric("Rows returned", len(results_df))

    if results_df.empty:
        st.info(
            "The query executed successfully, but no records were returned."
        )
    else:
        st.dataframe(
            results_df,
            hide_index=True,
            width="stretch",
            height=450,
        )

        csv_data = results_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇ Download results as CSV",
            data=csv_data,
            file_name="cricbuzz_sql_analytics.csv",
            mime="text/csv",
        )
