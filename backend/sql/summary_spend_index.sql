-- Optional performance index for the user-facing spend summary endpoints.
--
-- The LiteLLM_SpendLogs table is owned and migrated by LiteLLM itself.
-- This service only reads from it. Run this script once against the
-- LiteLLM PostgreSQL database to add a composite index that accelerates
-- the per-user summary query used by GET /me/spend/summary, /me/budget,
-- /me/spend/by-model, /me/spend/by-project and /me/spend/daily.
--
-- Without this index, those endpoints trigger a sequential scan of
-- LiteLLM_SpendLogs (~7s on a moderately-sized database) because the
-- single-column indexes on (api_key) and ("startTime") cannot both be
-- used in a single query.
--
-- The leading column of the composite is api_key because all user-facing
-- endpoints filter by api_key first and then by a startTime range. The
-- companion index in management_spend_index.sql has startTime as the
-- leading column because the management endpoint filters by a date
-- range first and groups by (api_key, day, model).
--
-- Safe to re-run (IF NOT EXISTS). Does not lock the table for writes
-- (CONCURRENTLY avoids blocking LiteLLM inserts).
--
-- Usage:
--   psql "$DATABASE_URL" -f sql/summary_spend_index.sql
-- or against the RDS host directly.

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_spend_logs_apikey_starttime
    ON "LiteLLM_SpendLogs"(api_key, "startTime");
