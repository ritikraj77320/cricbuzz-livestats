# Cricbuzz LiveStats — API Documentation

## 1. Overview

Cricbuzz LiveStats integrates with the Cricbuzz API through RapidAPI to retrieve live cricket match information and match scorecards.

The API integration is implemented in:

`src/api/api_client.py`

The client uses Python's `requests` library to make HTTP GET requests and `python-dotenv` to load API configuration from environment variables.

## 2. Authentication and Configuration

The API client reads the following environment variables:

| Variable | Purpose |
|---|---|
| `RAPIDAPI_KEY` | Authenticates requests to the API provider |
| `RAPIDAPI_HOST` | Identifies the RapidAPI host |

The client calls `load_dotenv()` to load environment variables from the project's `.env` file.

The base URL is constructed using the configured host:

`https://{RAPIDAPI_HOST}`

Requests include these headers:

- `X-RapidAPI-Key`: API authentication key.
- `X-RapidAPI-Host`: API host identifier.

**Security:** Keep the real API key in `.env`. Never commit the actual key to a public GitHub repository.

## 3. API Functions

### 3.1 Fetch Live Matches

**Function:** `get_live_matches()`

**Endpoint:**

`GET /matches/v1/live`

**Purpose:**

Retrieves the live-match response from the Cricbuzz API.

**Implementation flow:**

1. Checks whether `RAPIDAPI_KEY` and `RAPIDAPI_HOST` are configured.
2. Constructs the live-matches endpoint URL.
3. Adds the RapidAPI authentication headers.
4. Sends an HTTP GET request with a 30-second timeout.
5. Calls `raise_for_status()` to raise an exception for unsuccessful HTTP status codes.
6. Returns the response as JSON.

**Possible error conditions:**

- Missing API key or host configuration raises `ValueError`.
- HTTP errors raise exceptions through `response.raise_for_status()`.
- Network errors and timeouts may raise exceptions from `requests`.
- Invalid JSON may raise a JSON decoding exception.

### 3.2 Fetch Match Scorecard

**Function:** `get_match_scorecard(match_id)`

**Endpoint:**

`GET /mcenter/v1/{match_id}/scard`

**Parameter:**

- `match_id`: The Cricbuzz match identifier used to request the scorecard.

**Purpose:**

Retrieves the scorecard response for a specified match.

**Implementation flow:**

1. Checks whether the API key and host are configured.
2. Inserts the supplied match ID into the scorecard endpoint.
3. Adds the RapidAPI authentication headers.
4. Sends an HTTP GET request with a 30-second timeout.
5. Raises an exception for unsuccessful HTTP responses.
6. Returns the response as JSON.

**Possible error conditions:**

- Missing API configuration.
- HTTP errors, including unsuccessful API responses.
- Network failures and request timeouts.
- JSON decoding errors.

## 4. Data Flow

The API integration follows this general flow:

1. The application or synchronization pipeline calls an API client function.
2. The client sends an authenticated HTTP GET request.
3. The API provider returns a JSON response.
4. The response is passed to the calling module.
5. The scorecard parser extracts supported cricket statistics.
6. The database importer stores the parsed data in PostgreSQL.

The live-matches response is used to discover matches, while the scorecard endpoint supplies match-level scoring information.

## 5. Error Handling and Timeouts

Both API functions use a 30-second request timeout to avoid waiting indefinitely for a response.

Both functions call `response.raise_for_status()`, which surfaces unsuccessful HTTP responses as exceptions.

The current API client does not implement explicit retry logic, rate-limit handling, custom exception classes, or response caching. These can be added in a future improvement.

## 6. API Limitations

The API client returns the provider's JSON response without validating its complete structure.

The exact fields available depend on the provider response. Parsing and database-import modules are responsible for interpreting the fields needed by the application.

API availability, endpoint behavior, rate limits, and subscription restrictions depend on the configured provider and RapidAPI plan.

## 7. Future Improvements

Potential improvements include:

- Add structured logging for API requests and failures.
- Handle HTTP 429 rate-limit responses.
- Add controlled retries with exponential backoff for transient failures.
- Validate API response structures before parsing.
- Add automated tests using mocked HTTP responses.
- Add API caching where appropriate.
- Avoid logging API credentials or other secrets.
