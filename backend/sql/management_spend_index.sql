-- Optional performance index for the management spend endpoint.
--
-- The LiteLLM_SpendLogs table is owned and migrated by LiteLLM itself.
-- This service only reads from it. Run this script once against the
-- LiteLLM PostgreSQL database to add a composite covering index that
-- accelerates the management aggregation query, which filters by a
-- startTime range and groups by (api_key, day, model).
--
-- Safe to re-run (IF NOT EXISTS). Does not lock the table for writes
-- (CONCURRENTLY avoids blocking LiteLLM inserts).
--
-- Usage:
--   psql "$DATABASE_URL" -f sql/management_spend_index.sql
-- or against the RDS host directly.

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_spend_logs_starttime_apikey_model
    ON "LiteLLM_SpendLogs"("startTime", api_key, model);
