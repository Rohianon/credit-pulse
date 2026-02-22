-- Task 3: SQL Analysis Queries on sql_extract.xlsx data
-- ==========================================================

-- Query 1: Count total records and distinct users
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT user_id) AS distinct_users
FROM raw_sql_extract;

-- Query 2: Latest record per user by ex_date
SELECT *
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ex_date DESC) AS rn
    FROM raw_sql_extract
)
WHERE rn = 1
ORDER BY user_id;

-- Query 3: Top 5 users with the most records
SELECT
    user_id,
    COUNT(*) AS record_count
FROM raw_sql_extract
GROUP BY user_id
ORDER BY record_count DESC
LIMIT 5;

-- Query 4: Records count per day
SELECT
    CAST(ex_date AS DATE) AS record_date,
    COUNT(*) AS daily_count
FROM raw_sql_extract
GROUP BY CAST(ex_date AS DATE)
ORDER BY record_date;
