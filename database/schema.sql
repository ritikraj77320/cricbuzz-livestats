
CREATE TABLE teams (
    team_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(100)
);


CREATE TABLE players (
    player_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    player_name VARCHAR(150) NOT NULL,
    date_of_birth DATE,
    role VARCHAR(50),
    provider_player_id VARCHAR(100) UNIQUE
);


CREATE TABLE venues (
    venue_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venue_name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    provider_venue_id VARCHAR(100) UNIQUE
);


CREATE TABLE series (
    series_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    series_name VARCHAR(200) NOT NULL,
    start_date DATE,
    end_date DATE,
    provider_series_id VARCHAR(100) UNIQUE,
    CONSTRAINT chk_series_dates
        CHECK (
            start_date IS NULL
            OR end_date IS NULL
            OR end_date >= start_date
        )
);


CREATE TABLE matches (
    match_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    series_id BIGINT NOT NULL REFERENCES series(series_id),
    venue_id BIGINT REFERENCES venues(venue_id),
    team1_id BIGINT NOT NULL REFERENCES teams(team_id),
    team2_id BIGINT NOT NULL REFERENCES teams(team_id),
    match_name VARCHAR(150),
    match_format VARCHAR(30),
    start_time TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'Scheduled',
    provider_match_id VARCHAR(100) UNIQUE,

    CONSTRAINT chk_different_teams
        CHECK (team1_id <> team2_id)
);

CREATE TABLE innings (
    innings_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(match_id),
    batting_team_id BIGINT NOT NULL REFERENCES teams(team_id),
    innings_number SMALLINT NOT NULL,
    total_runs INTEGER NOT NULL DEFAULT 0,
    wickets SMALLINT NOT NULL DEFAULT 0,
    legal_balls INTEGER NOT NULL DEFAULT 0,
    extras INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT chk_innings_number
        CHECK (innings_number > 0),

    CONSTRAINT chk_innings_runs
        CHECK (total_runs >= 0),

    CONSTRAINT chk_innings_wickets
        CHECK (wickets BETWEEN 0 AND 10),

    CONSTRAINT chk_innings_balls
        CHECK (legal_balls >= 0),

    CONSTRAINT chk_innings_extras
        CHECK (extras >= 0),

    CONSTRAINT uq_match_innings
        UNIQUE (match_id, innings_number)
);


CREATE TABLE batting_performances (
    batting_performance_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    innings_id BIGINT NOT NULL REFERENCES innings(innings_id),
    player_id BIGINT NOT NULL REFERENCES players(player_id),
    runs INTEGER NOT NULL DEFAULT 0,
    balls_faced INTEGER NOT NULL DEFAULT 0,
    fours INTEGER NOT NULL DEFAULT 0,
    sixes INTEGER NOT NULL DEFAULT 0,
    dismissal VARCHAR(150),

    CONSTRAINT chk_batting_runs
        CHECK (runs >= 0),

    CONSTRAINT chk_batting_balls
        CHECK (balls_faced >= 0),

    CONSTRAINT chk_batting_fours
        CHECK (fours >= 0),

    CONSTRAINT chk_batting_sixes
        CHECK (sixes >= 0),

    CONSTRAINT uq_batter_per_innings
        UNIQUE (innings_id, player_id)
);


CREATE TABLE bowling_performances (
    bowling_performance_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    innings_id BIGINT NOT NULL REFERENCES innings(innings_id),
    player_id BIGINT NOT NULL REFERENCES players(player_id),
    legal_balls INTEGER NOT NULL DEFAULT 0,
    maidens INTEGER NOT NULL DEFAULT 0,
    runs_conceded INTEGER NOT NULL DEFAULT 0,
    wickets INTEGER NOT NULL DEFAULT 0,
    economy NUMERIC(5, 2),

    CONSTRAINT chk_bowling_balls
        CHECK (legal_balls >= 0),

    CONSTRAINT chk_bowling_maidens
        CHECK (maidens >= 0),

    CONSTRAINT chk_bowling_runs
        CHECK (runs_conceded >= 0),

    CONSTRAINT chk_bowling_wickets
        CHECK (wickets >= 0 AND wickets <= 10),

    CONSTRAINT chk_bowling_economy
        CHECK (economy IS NULL OR economy >= 0),

    CONSTRAINT uq_bowler_per_innings
        UNIQUE (innings_id, player_id)
);


CREATE TABLE fielding_performances (
    fielding_performance_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    innings_id BIGINT NOT NULL REFERENCES innings(innings_id),
    player_id BIGINT NOT NULL REFERENCES players(player_id),
    catches INTEGER NOT NULL DEFAULT 0,
    stumpings INTEGER NOT NULL DEFAULT 0,
    run_outs INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT chk_fielding_catches
        CHECK (catches >= 0),

    CONSTRAINT chk_fielding_stumpings
        CHECK (stumpings >= 0),

    CONSTRAINT chk_fielding_run_outs
        CHECK (run_outs >= 0),

    CONSTRAINT uq_fielder_per_innings
        UNIQUE (innings_id, player_id)
);


CREATE TABLE batting_partnerships (
    partnership_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    innings_id BIGINT NOT NULL REFERENCES innings(innings_id),
    batter1_id BIGINT NOT NULL REFERENCES players(player_id),
    batter2_id BIGINT NOT NULL REFERENCES players(player_id),
    partnership_runs INTEGER NOT NULL DEFAULT 0,
    partnership_balls INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT chk_partnership_runs
        CHECK (partnership_runs >= 0),

    CONSTRAINT chk_partnership_balls
        CHECK (partnership_balls >= 0),

    CONSTRAINT chk_different_batters
        CHECK (batter1_id <> batter2_id)
);
