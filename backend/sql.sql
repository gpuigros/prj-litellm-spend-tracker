SET TIME ZONE 'UTC';

-- 0. Key lookup — find your key by alias (no pgcrypto needed)
SELECT token, user_id, key_alias, max_budget, spend, budget_limits, budget_duration, budget_reset_at
FROM "LiteLLM_VerificationToken"
WHERE key_alias = 'engineering';

-- 1. Summary — spend within the current budget window (from budget_limits JSONB)
--    This is what LiteLLM actually enforces, NOT calendar month.
SELECT k.key_alias,
       bl.max_budget,
       bl.budget_duration,
       bl.reset_at AS budget_reset_at,
       bl.reset_at - (bl.budget_duration::text || ' day')::interval AS window_start,
       k.spend AS litellm_counter,
       ROUND(COALESCE(w.window_spend, 0)::numeric, 4) AS window_spend,
       ROUND((bl.max_budget - COALESCE(w.window_spend, 0))::numeric, 4) AS remaining,
       ROUND((COALESCE(w.window_spend, 0) / NULLIF(bl.max_budget, 0) * 100)::numeric, 2) AS used_percent
FROM "LiteLLM_VerificationToken" k
CROSS JOIN LATERAL (
    SELECT (elem ->> 'max_budget')::float      AS max_budget,
           (elem ->> 'budget_duration')        AS budget_duration,
           (elem ->> 'reset_at')::timestamptz  AS reset_at
    FROM jsonb_array_elements(k.budget_limits) AS elem
    LIMIT 1
) bl
LEFT JOIN LATERAL (
    SELECT SUM(s.spend) AS window_spend,
           COUNT(*)     AS requests
    FROM "LiteLLM_SpendLogs" s
    WHERE s.api_key = k.token
      AND s."startTime" >= bl.reset_at - (bl.budget_duration::text || ' day')::interval
      AND s."startTime" <  bl.reset_at
) w ON true
WHERE k.key_alias = 'engineering';

-- 2. By model — within the current budget window
SELECT s.model,
       ROUND(SUM(s.spend)::numeric, 4)  AS spend,
       COUNT(*)                         AS requests,
       COALESCE(SUM(s.total_tokens), 0) AS tokens
FROM "LiteLLM_SpendLogs" s
JOIN "LiteLLM_VerificationToken" k ON s.api_key = k.token
CROSS JOIN LATERAL (
    SELECT (elem ->> 'budget_duration')        AS budget_duration,
           (elem ->> 'reset_at')::timestamptz  AS reset_at
    FROM jsonb_array_elements(k.budget_limits) AS elem
    LIMIT 1
) bl
WHERE k.key_alias = 'engineering'
  AND s."startTime" >= bl.reset_at - (bl.budget_duration::text || ' day')::interval
  AND s."startTime" <  bl.reset_at
  AND s.model IS NOT NULL AND s.model <> ''
GROUP BY s.model
ORDER BY spend DESC;

-- 3. Daily trend — within the current budget window
SELECT DATE(s."startTime") AS date,
       ROUND(SUM(s.spend)::numeric, 4)  AS spend,
       COUNT(*)                         AS requests,
       COALESCE(SUM(s.total_tokens), 0) AS tokens
FROM "LiteLLM_SpendLogs" s
JOIN "LiteLLM_VerificationToken" k ON s.api_key = k.token
CROSS JOIN LATERAL (
    SELECT (elem ->> 'budget_duration')        AS budget_duration,
           (elem ->> 'reset_at')::timestamptz  AS reset_at
    FROM jsonb_array_elements(k.budget_limits) AS elem
    LIMIT 1
) bl
WHERE k.key_alias = 'engineering'
  AND s."startTime" >= bl.reset_at - (bl.budget_duration::text || ' day')::interval
  AND s."startTime" <  bl.reset_at
GROUP BY DATE(s."startTime")
ORDER BY DATE(s."startTime");

-- 4. Comparison: budget window vs calendar month (to see the gap)
SELECT
    ROUND(COALESCE(bw.window_spend, 0)::numeric, 4) AS budget_window_spend,
    ROUND(COALESCE(cal.month_spend, 0)::numeric, 4) AS calendar_month_spend,
    ROUND((COALESCE(bw.window_spend, 0) - COALESCE(cal.month_spend, 0))::numeric, 4) AS difference,
    bl.max_budget,
    bl.budget_duration,
    bl.reset_at AS budget_reset_at
FROM "LiteLLM_VerificationToken" k
CROSS JOIN LATERAL (
    SELECT (elem ->> 'max_budget')::float      AS max_budget,
           (elem ->> 'budget_duration')        AS budget_duration,
           (elem ->> 'reset_at')::timestamptz  AS reset_at
    FROM jsonb_array_elements(k.budget_limits) AS elem
    LIMIT 1
) bl
LEFT JOIN LATERAL (
    SELECT SUM(s.spend) AS window_spend
    FROM "LiteLLM_SpendLogs" s
    WHERE s.api_key = k.token
      AND s."startTime" >= bl.reset_at - (bl.budget_duration::text || ' day')::interval
      AND s."startTime" <  bl.reset_at
) bw ON true
LEFT JOIN LATERAL (
    SELECT SUM(s.spend) AS month_spend
    FROM "LiteLLM_SpendLogs" s
    WHERE s.api_key = k.token
      AND s."startTime" >= date_trunc('month', NOW())
      AND s."startTime" <= (date_trunc('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 second')
) cal ON true
WHERE k.key_alias = 'engineering';