# Cricbuzz LiveStats — Database Documentation

## 1. Overview

Cricbuzz LiveStats uses PostgreSQL to store cricket match information, teams, players, venues, series, innings, and player performance statistics.

The database schema is defined in `database/schema.sql`.

The schema contains ten tables:

1. `teams`
2. `players`
3. `venues`
4. `series`
5. `matches`
6. `innings`
7. `batting_performances`
8. `bowling_performances`
9. `fielding_performances`
10. `batting_partnerships`

## 2. Table Descriptions

### 2.1 `teams`

Stores cricket team information.

| Column | Description |
|---|---|
| `team_id` | Primary key, generated automatically |
| `team_name` | Required and unique team name |
| `country` | Country associated with the team |

### 2.2 `players`

Stores player information.

| Column | Description |
|---|---|
| `player_id` | Primary key |
| `player_name` | Required player name |
| `date_of_birth` | Optional date of birth |
| `role` | Optional player role |
| `provider_player_id` | Optional unique external provider ID |

### 2.3 `venues`

Stores match venue information.

| Column | Description |
|---|---|
| `venue_id` | Primary key |
| `venue_name` | Required venue name |
| `city` | Venue city |
| `country` | Venue country |
| `provider_venue_id` | Optional unique provider ID |

### 2.4 `series`

Stores cricket series information.

| Column | Description |
|---|---|
| `series_id` | Primary key |
| `series_name` | Required series name |
| `start_date` | Series start date |
| `end_date` | Series end date |
| `provider_series_id` | Optional unique provider ID |

The schema prevents the end date from being earlier than the start date when both dates are provided.

### 2.5 `matches`

Stores match-level information.

| Column | Description |
|---|---|
| `match_id` | Primary key |
| `series_id` | Required foreign key to `series` |
| `venue_id` | Optional foreign key to `venues` |
| `team1_id` | Required foreign key to `teams` |
| `team2_id` | Required foreign key to `teams` |
| `match_name` | Match name or description |
| `match_format` | Match format |
| `start_time` | Match start timestamp with time zone |
| `status` | Match status; defaults to `Scheduled` |
| `provider_match_id` | Optional unique external provider ID |

A check constraint prevents a team from being assigned as both participating teams in the same match.

### 2.6 `innings`

Stores each innings associated with a match.

| Column | Description |
|---|---|
| `innings_id` | Primary key |
| `match_id` | Foreign key to `matches` |
| `batting_team_id` | Foreign key to `teams` |
| `innings_number` | Positive innings number |
| `total_runs` | Total runs; defaults to zero |
| `wickets` | Wickets lost, constrained to 0–10 |
| `legal_balls` | Number of legal balls |
| `extras` | Total extras |

The combination of `match_id` and `innings_number` is unique, preventing duplicate innings numbers for the same match.

### 2.7 `batting_performances`

Stores batting statistics for each player in an innings.

| Column | Description |
|---|---|
| `batting_performance_id` | Primary key |
| `innings_id` | Foreign key to `innings` |
| `player_id` | Foreign key to `players` |
| `runs` | Runs scored |
| `balls_faced` | Balls faced |
| `fours` | Number of fours |
| `sixes` | Number of sixes |
| `dismissal` | Dismissal description |

The pair `innings_id` and `player_id` is unique. Runs, balls, fours, and sixes must be non-negative.

### 2.8 `bowling_performances`

Stores bowling statistics for each player in an innings.

| Column | Description |
|---|---|
| `bowling_performance_id` | Primary key |
| `innings_id` | Foreign key to `innings` |
| `player_id` | Foreign key to `players` |
| `legal_balls` | Legal balls bowled |
| `maidens` | Maiden overs |
| `runs_conceded` | Runs conceded |
| `wickets` | Wickets credited to the bowler |
| `economy` | Bowling economy rate |

The pair `innings_id` and `player_id` is unique. Check constraints prevent negative statistics and restrict wickets to 0–10.

### 2.9 `fielding_performances`

Stores fielding contributions for each player in an innings.

| Column | Description |
|---|---|
| `fielding_performance_id` | Primary key |
| `innings_id` | Foreign key to `innings` |
| `player_id` | Foreign key to `players` |
| `catches` | Number of catches |
| `stumpings` | Number of stumpings |
| `run_outs` | Number of run-outs |

The pair `innings_id` and `player_id` is unique. Each fielding statistic must be non-negative.

The scorecard parser extracts fielding contributions from dismissal descriptions where supported by the API response.

### 2.10 `batting_partnerships`

Stores batting partnership statistics for an innings.

| Column | Description |
|---|---|
| `partnership_id` | Primary key |
| `innings_id` | Foreign key to `innings` |
| `batter1_id` | Foreign key to `players` |
| `batter2_id` | Foreign key to `players` |
| `partnership_runs` | Partnership runs |
| `partnership_balls` | Partnership balls |

Partnership runs and balls must be non-negative. The schema prevents the same player ID from being assigned to both batter columns in a single partnership record.

## 3. Entity Relationships

The main relationships are:

- One series can contain many matches.
- One venue can host many matches.
- Each match references two teams.
- One match can contain multiple innings.
- Each innings references its batting team.
- An innings can have multiple batting, bowling, and fielding performance records.
- Each performance record references a player.
- An innings can have multiple batting partnerships, each referencing two players.

## 4. Primary Keys and Foreign Keys

Every table has a generated identity primary key.

Foreign keys maintain referential integrity between matches, series, venues, teams, innings, players, and performance records.

Unique constraints are used for team names and external provider IDs where defined. Additional uniqueness constraints prevent duplicate batting, bowling, and fielding records for the same player in the same innings.

## 5. Data Integrity Rules

The schema defines check constraints to enforce:

- Different participating teams for each match.
- Valid series date ordering when both dates exist.
- Positive innings numbers.
- Non-negative innings totals, balls, and extras.
- Wickets within the range of 0–10.
- Non-negative batting statistics.
- Non-negative bowling statistics and economy values.
- Non-negative fielding statistics.
- Non-negative partnership runs and balls.
- Different batter IDs within a partnership.

## 6. Database Initialization

To initialize the database:

1. Install and start PostgreSQL.
2. Create the `cricbuzz_livestats` database.
3. Connect to the database using your PostgreSQL client.
4. Execute the SQL statements in `database/schema.sql`.
5. Configure the application's database connection settings.
6. Run the project's verification queries from `database/verification.sql`.

Do not rerun schema creation statements against an existing populated database unless you understand their effects and have a backup.

## 7. Validation

The project includes `database/verification.sql` for database checks.

The developer has also verified scorecard import behavior for a completed match, including fielding records, and tested the SQL analytics catalog.

## 8. Future Improvements

Potential database improvements include:

- Indexes for frequently filtered foreign-key columns.
- More comprehensive uniqueness constraints for partnership records.
- Dedicated provider identifiers for fielders when available from the API.
- Automated data-quality checks for duplicate players and incomplete scorecards.
- Database migration scripts for safely evolving the schema.
