# Cricbuzz LiveStats

A cricket statistics and analytics application built with Python, Streamlit, PostgreSQL, and the Cricbuzz API.

## Project Overview

Cricbuzz LiveStats retrieves cricket match data from a Cricbuzz API provider, stores structured match and player information in PostgreSQL, and presents cricket statistics through an interactive Streamlit application.

## Features

- **Live Matches:** View match information retrieved from the API.
- **Player Statistics:** Explore recorded batting and bowling performances.
- **SQL Analytics:** Execute predefined, read-only analytics queries covering matches, batting, bowling, players, teams, fielding, partnerships, and advanced SQL analysis.
- **Player Management:** Manage player records through the application.
- **Scorecard Import:** Parse and import innings, batting, bowling, extras, partnerships, and fielding contributions.
- **PostgreSQL Database:** Store structured cricket data and relationships.
- **Data Validation:** Test scorecard parsing, database operations, and SQL analytics.

## Technology Stack

- **Language:** Python
- **Frontend:** Streamlit
- **Database:** PostgreSQL
- **Data access:** SQLAlchemy and PostgreSQL database connectivity
- **Data processing:** Pandas
- **API integration:** HTTP requests to the configured Cricbuzz API provider
- **Testing:** Python test scripts

## Project Structure


cricbuzz-livestats/
├── app.py
├── pages/
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
│   ├── architecture.md
│   ├── database.md
│   └── api.md
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md


## Prerequisites

- Python installed
- PostgreSQL installed and running
- A valid API subscription and credentials for the configured Cricbuzz API provider
- Git, if you want to clone or version-control the project

## Installation

1. Clone the repository or download the project source.
2. Open the project directory in a terminal.
3. Create and activate a virtual environment.
4. Install the dependencies.
5. Create a PostgreSQL database.
6. Configure the environment variables.
7. Initialize the database schema.
8. Start the Streamlit application.

Example commands for Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Create a local `.env` file using `.env.example` as a reference.

Configure the API credentials and PostgreSQL connection settings using the variable names expected by the application.

**Never commit your actual API key, database password, or other secrets to GitHub.**

## Database

The database schema is maintained in `database/schema.sql`. The project stores match information, teams, venues, series, innings, players, batting performances, bowling performances, fielding performances, and batting partnerships.

Use `database/verification.sql` to run the database checks defined for the project.

## Running Scorecard Imports

The scorecard importer can retrieve match IDs from the configured live-matches API response and import available scorecards.

Run it from the project root:

```powershell
python -m src.database.import_scorecard
```

The importer depends on the configured API credentials, database connection, and the match records already present in PostgreSQL.

## Testing

The `tests/` directory contains test scripts for API access, database access, scorecard parsing, fielding parsing, player statistics, repository operations, and SQL analytics.

Run individual test scripts using Python from the project root. Confirm the required environment variables and database are configured before running integration tests.

## Current Validation

- Four Streamlit pages have been tested by the developer.
- All 32 predefined SQL analytics queries have been verified by the developer.
- Fielding import was tested using a completed match scorecard.
- Reimporting that scorecard preserved the verified fielding totals.

## Security

- Keep `.env` out of version control.
- Use `.env.example` with placeholder values.
- Do not commit virtual environments, Python cache folders, or unnecessary debug responses.
- Validate and handle API failures and incomplete scorecards.

## Future Improvements

- Automated scheduled scorecard synchronization
- Improved API retry and rate-limit handling
- More comprehensive automated tests
- Enhanced match-specific and player-specific analytics
- Deployment and production configuration

## License

Add a license before distributing the project publicly. If no license is specified, do not assume others have permission to reuse the code.
