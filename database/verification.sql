
-- 1. List all project tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;


-- 2. Inspect the columns of every project table
SELECT
    table_name,
    ordinal_position,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'teams',
      'players',
      'venues',
      'series',
      'matches',
      'innings',
      'batting_performances',
      'bowling_performances',
      'fielding_performances',
      'batting_partnerships'
  )
ORDER BY table_name, ordinal_position;


-- 3. List foreign-key relationships
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
   AND tc.constraint_schema = kcu.constraint_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
   AND ccu.constraint_schema = tc.constraint_schema
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name, kcu.column_name;

SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'teams',
      'venues',
      'series',
      'matches'
  )
ORDER BY table_name, ordinal_position;


-- 1. Count records in player performance tables
SELECT 'players' AS table_name, COUNT(*) AS record_count
FROM players
UNION ALL
SELECT 'batting_performances', COUNT(*)
FROM batting_performances
UNION ALL
SELECT 'bowling_performances', COUNT(*)
FROM bowling_performances
ORDER BY table_name;


-- 2. Inspect batting performance records
SELECT *
FROM batting_performances
ORDER BY player_id
LIMIT 20;


-- 3. Inspect bowling performance records
SELECT *
FROM bowling_performances
ORDER BY player_id
LIMIT 20;


-- 4. Check whether player records are linked to teams
SELECT player_id, player_name, role, provider_player_id
FROM players
ORDER BY player_id
LIMIT 20;
