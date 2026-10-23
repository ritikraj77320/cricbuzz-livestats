# Cricbuzz LiveStats — System Architecture

## 1. Overview

Cricbuzz LiveStats is a Python-based cricket statistics and analytics application. It uses Streamlit for the user interface, a Cricbuzz API provider for match data, and PostgreSQL for persistent storage.

## 2. Application Layers

### Presentation Layer

The `pages/` directory contains four Streamlit pages:

- Live Matches
- Player Statistics
- SQL Analytics
- Player Management

The root `app.py` provides the main Streamlit application entry point.

### Application Logic Layer

The `src/` directory contains the application's processing and integration logic.

- `src/api/`: API communication and scorecard parsing.
- `src/analytics/`: Player statistics and predefined SQL analytics.
- `src/database/`: Database connectivity, synchronization, and import operations.
- `src/sync_pipeline.py`: Synchronization pipeline entry point.

### Database Layer

PostgreSQL stores structured cricket data. The database schema is defined in `database/schema.sql`, and verification queries are provided in `database/verification.sql`.

### External API Layer

The configured Cricbuzz API provider supplies match and scorecard information. API access requires valid configuration and credentials.

## 3. Scorecard Data Flow

The scorecard import process follows this general sequence:

1. Retrieve the live-matches response.
2. Extract match identifiers.
3. Request a scorecard for each selected match.
4. Parse the response into structured Python data.
5. Resolve the relevant match, team, player, and innings records.
6. Import batting, bowling, extras, partnerships, and parsed fielding contributions.
7. Commit the database transaction.
8. Make stored records available to analytics queries.

If an import fails, the importer rolls back the database transaction and reports the error.

## 4. Analytics Flow

1. A user opens the SQL Analytics page.
2. The application selects a predefined query from the query catalog.
3. The analytics module validates the category, query name, and result limit.
4. SQLAlchemy executes the approved query against PostgreSQL.
5. Pandas converts the result into a DataFrame.
6. Streamlit displays the results.

The query catalog is designed for read-only analytics queries.

## 5. Database Entities

The project includes tables for:

- Matches
- Series
- Teams
- Venues
- Players
- Innings
- Batting performances
- Bowling performances
- Fielding performances
- Batting partnerships

Foreign keys and constraints defined in the actual database schema govern the relationships between these entities.

## 6. Configuration and Security

Sensitive configuration belongs in the local `.env` file. The `.env` file must not be committed to version control.

The application should handle API errors, incomplete scorecards, database failures, and invalid input without exposing credentials.

## 7. Testing and Validation

The `tests/` directory contains test scripts for API access, database access, parsing, player operations, player statistics, and SQL analytics.

The developer has verified all 32 predefined SQL analytics queries and tested fielding import and reimport behavior using a completed match scorecard.

## 8. Known Limitations

- API availability, rate limits, and scorecard completeness depend on the configured provider.
- Fielding attribution depends on the dismissal information returned by the API.
- A successful import of one completed match does not guarantee every match or every API response will import successfully.
- Production deployment requires separate validation of credentials, database access, and runtime configuration.