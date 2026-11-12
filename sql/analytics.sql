-- 1. Overall query statistics
SELECT
    COUNT(*) AS total_queries,
    ROUND(100.0 * AVG(cache_hit), 2) AS cache_hit_pct,
    ROUND(100.0 * AVG(refused), 2) AS refused_pct
FROM query_log;


-- 2. Cached vs uncached latency (answered requests only)
SELECT
    CASE
        WHEN cache_hit = 1 THEN 'Cached'
        ELSE 'Uncached'
    END AS request_type,
    COUNT(*) AS total_requests,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms,
    ROUND(MIN(latency_ms), 2) AS min_latency_ms,
    ROUND(MAX(latency_ms), 2) AS max_latency_ms
FROM query_log
WHERE refused = 0
GROUP BY cache_hit;


-- 3. Daily query statistics
SELECT
    DATE(ts) AS query_date,
    COUNT(*) AS total_queries,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms
FROM query_log
GROUP BY DATE(ts)
ORDER BY query_date;


-- 4. Least confident answered questions
SELECT
    question,
    top_score,
    latency_ms
FROM query_log
WHERE refused = 0
ORDER BY top_score ASC
LIMIT 10;


-- 5. Most refused questions
SELECT
    question,
    COUNT(*) AS refusal_count
FROM query_log
WHERE refused = 1
GROUP BY question
ORDER BY refusal_count DESC
LIMIT 10;