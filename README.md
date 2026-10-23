# 🏏 Cricbuzz LiveStats

A cricket statistics and analytics application built with **Python, Streamlit, PostgreSQL, and the Cricbuzz API**. The project brings match information, player performance data, SQL analytics, and player-record management into one interactive application.

**GitHub Repository:** [ritikraj77320/cricbuzz-livestats](https://github.com/ritikraj77320/cricbuzz-livestats)

---

## 📌 Project Overview

Cricbuzz LiveStats retrieves cricket data through a configured Cricbuzz API provider, works with structured information in PostgreSQL, and presents features through a Streamlit interface. It demonstrates API integration, relational database design, SQL querying, Python data processing, and multi-page web application development.

## ✨ Features

- **Live Matches** — View match information retrieved from the configured API.
- **Player Statistics** — Explore recorded batting and bowling performance data.
- **SQL Analytics** — Run predefined, read-only analytical queries for matches, players, teams, batting, bowling, fielding, partnerships, and other supported analyses.
- **Player Management** — Use the application interface to work with player records.
- **Scorecard Import** — Parse and import supported scorecard information, including innings, batting, bowling, extras, partnerships, and fielding contributions.
- **PostgreSQL Database** — Store structured cricket data and related records.
- **Validation and Tests** — Test supported scorecard parsing, database operations, and SQL analytics.

> Available data and functionality depend on API access, database configuration, and which records have been imported.

## 🧰 Technology Stack

| Area | Technologies |
|---|---|
| Language | Python |
| Web interface | Streamlit |
| Database | PostgreSQL |
| Database access | SQLAlchemy, psycopg |
| Data processing | Pandas |
| API integration | HTTP requests, configured Cricbuzz API provider |
| Configuration | Environment variables / `.env` |
| Testing | Python test scripts |

## 📂 Project Structure

```text
cricbuzz-livestats/
├── app.py
├── pages/
│   ├── 1_🏏_Live_Matches.py
│   ├── 2_🏆_Player_Statistics.py
│   ├── 3_📊_SQL_Analytics.py
│   └── 4_👥_Player_Management.py
├── src/
│   ├── api/
│   ├── analytics/
│   ├── database/
│   └── sync_pipeline.py
├── database/
│   ├── schema.sql
│   └── verification.sql
├── data/
│   └── raw/
├── docs/
│   ├── api.md
│   ├── architecture.md
│   └── database.md
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## ✅ Prerequisites

Before running the application, install or arrange access to:

- Python (a version compatible with the packages in `requirements.txt`)
- PostgreSQL, locally or on a hosted PostgreSQL service
- API credentials for the configured Cricbuzz API provider
- Git (optional, for cloning the repository)

## 🚀 Installation and Setup

### 1. Clone the repository

```powershell
git clone https://github.com/ritikraj77320/cricbuzz-livestats.git
cd cricbuzz-livestats
```

Alternatively, download the repository ZIP from GitHub and extract it.

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, follow your system's Python environment policy or activate the environment using the terminal you normally use.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create a PostgreSQL database

Start PostgreSQL and create a database named `cricbuzz_livestats` (or choose another name and use it consistently in your configuration). For example, in `psql`:

```sql
CREATE DATABASE cricbuzz_livestats;
```

### 5. Configure environment variables

Create a local `.env` file in the project root, using `.env.example` as a reference. The application code currently uses these variable names:

```dotenv
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=your_rapidapi_host_here

DB_HOST=localhost
DB_PORT=5432
DB_NAME=cricbuzz_livestats
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
```

Replace the placeholders with your own values. The API host must match the host required by your configured API provider. If using a hosted PostgreSQL database, use the host and credentials supplied by that provider rather than `localhost`.

**Never commit `.env`, real API keys, database passwords, or other credentials to GitHub.** Keep `.env.example` limited to placeholder values.

### 6. Initialize the database schema

Run the SQL in `database/schema.sql` against the database you configured. You can use `psql`, pgAdmin, or your PostgreSQL provider's SQL editor. For example, from a terminal where `psql` is available:

```powershell
psql -U your_postgres_username -d cricbuzz_livestats -f database/schema.sql
```

Run the checks in `database/verification.sql` to verify the database objects and checks defined in that file.

### 7. Start the Streamlit application

From the project root, run:

```powershell
streamlit run app.py
```

Streamlit will provide a local URL in the terminal, typically `http://localhost:8501`.

## 🔄 Importing Scorecards

The scorecard importer can retrieve match IDs from the configured live-matches API response and import available scorecards. Run this command from the project root after configuring the API and database:

```powershell
python -m src.database.import_scorecard
```

The importer depends on valid API credentials, a working database connection, and the match records required by the import workflow.

## 🧪 Testing

The `tests/` directory contains scripts for areas such as API access, database access, scorecard parsing, fielding parsing, player statistics, repository operations, and SQL analytics.

Run an individual test script from the project root using Python. Before running integration tests, make sure the required environment variables are set and the database is available. Use the exact test filenames present in the repository.

## ✔️ Current Validation

The project README supplied for this update records the following developer validation:

- Four Streamlit pages have been tested.
- All 32 predefined SQL analytics queries have been verified.
- Fielding import has been tested using a completed match scorecard.
- Reimporting that scorecard preserved the verified fielding totals.

These checks describe the validation recorded by the developer; they do not imply that every deployment environment has been tested.

## 🔐 Security Notes

- Keep `.env` out of version control.
- Store only placeholder values in `.env.example`.
- Never expose API keys, database passwords, or connection strings in screenshots, videos, logs, or public repositories.
- Do not commit virtual environments, Python cache files, or sensitive API responses.
- Handle API failures, incomplete scorecards, and database connection errors gracefully.
- For a cloud deployment, configure secrets through the hosting platform and use a reachable hosted database; `localhost` in a cloud environment refers to that environment, not your personal computer.

## 🛣️ Future Improvements

- Scheduled scorecard synchronization
- More robust API retry and rate-limit handling
- Broader automated test coverage
- Additional match and player analytics
- Completed and verified cloud database and application deployment

## 📚 Documentation

- [`docs/api.md`](docs/api.md) — API integration details
- [`docs/architecture.md`](docs/architecture.md) — Application architecture and data flow
- [`docs/database.md`](docs/database.md) — Database structure and relationships

## 📄 License

No license is specified in this repository README. Add a license file if you intend to define how others may reuse, modify, or distribute this project. Without a license, others should not assume they have permission to reuse the code.

---

**Repository:** [https://github.com/ritikraj77320/cricbuzz-livestats](https://github.com/ritikraj77320/cricbuzz-livestats)
