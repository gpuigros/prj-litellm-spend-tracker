SET TIME ZONE 'UTC';

-- 0. Key lookup — find your key by alias (no pgcrypto needed)
--    The budget cap is the flat `max_budget` column on the key.
SELECT token, user_id, key_alias, max_budget, spend
FROM "LiteLLM_VerificationToken"
WHERE key_alias = 'engineering';

-- 1. Summary — calendar-month spend against the key's max_budget
--    The cap is the key's hard limit, not a rolling window.
SELECT k.key_alias,
       k.max_budget,
       k.spend AS litellm_counter,
       ROUND(COALESCE(cal.month_spend, 0)::numeric, 4) AS month_spend,
       ROUND((k.max_budget - COALESCE(cal.month_spend, 0))::numeric, 4) AS remaining,
       ROUND((COALESCE(cal.month_spend, 0) / NULLIF(k.max_budget, 0) * 100)::numeric, 2) AS used_percent
FROM "LiteLLM_VerificationToken" k
LEFT JOIN LATERAL (
    SELECT SUM(s.spend) AS month_spend
    FROM "LiteLLM_SpendLogs" s
    WHERE s.api_key = k.token
      AND s."startTime" >= date_trunc('month', NOW())
      AND s."startTime" <= (date_trunc('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 second')
) cal ON true
WHERE k.key_alias = 'engineering';

-- 2. By model — within the current calendar month
SELECT s.model,
       ROUND(SUM(s.spend)::numeric, 4)  AS spend,
       COUNT(*)                         AS requests,
       COALESCE(SUM(s.total_tokens), 0) AS tokens
FROM "LiteLLM_SpendLogs" s
JOIN "LiteLLM_VerificationToken" k ON s.api_key = k.token
WHERE k.key_alias = 'engineering'
  AND s."startTime" >= date_trunc('month', NOW())
  AND s."startTime" <= (date_trunc('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 second')
  AND s.model IS NOT NULL AND s.model <> ''
GROUP BY s.model
ORDER BY spend DESC;

-- 3. Daily trend — within the current calendar month
SELECT DATE(s."startTime") AS date,
       ROUND(SUM(s.spend)::numeric, 4)  AS spend,
       COUNT(*)                         AS requests,
       COALESCE(SUM(s.total_tokens), 0) AS tokens
FROM "LiteLLM_SpendLogs" s
JOIN "LiteLLM_VerificationToken" k ON s.api_key = k.token
WHERE k.key_alias = 'engineering'
  AND s."startTime" >= date_trunc('month', NOW())
  AND s."startTime" <= (date_trunc('month', NOW()) + INTERVAL '1 month' - INTERVAL '1 second')
GROUP BY DATE(s."startTime")
ORDER BY DATE(s."startTime");
