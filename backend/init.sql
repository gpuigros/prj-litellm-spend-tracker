-- Initialize LiteLLM database schema for testing
-- This simulates the tables that LiteLLM creates
-- Note: LiteLLM uses PascalCase table names and stores API keys as SHA-256 hashes

-- Spend logs table (matches LiteLLM's actual table name)
CREATE TABLE IF NOT EXISTS "LiteLLM_SpendLogs" (
    request_id VARCHAR(255) PRIMARY KEY,
    api_key VARCHAR(255) NOT NULL,
    "user" VARCHAR(255),
    model VARCHAR(255) NOT NULL,
    spend FLOAT NOT NULL DEFAULT 0.0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    call_type VARCHAR(50),
    metadata TEXT,
    cache_hit VARCHAR(10),
    cache_key VARCHAR(255),
    "startTime" TIMESTAMP NOT NULL,
    "endTime" TIMESTAMP NOT NULL
);

-- Virtual keys table (matches LiteLLM's actual table name)
-- IMPORTANT: The 'token' column stores SHA-256 hashes of the actual API keys
CREATE TABLE IF NOT EXISTS "LiteLLM_VerificationToken" (
    token VARCHAR(255) PRIMARY KEY,
    key_alias VARCHAR(255),
    spend FLOAT NOT NULL DEFAULT 0.0,
    max_budget FLOAT,
    user_id VARCHAR(255),
    team_id VARCHAR(255),
    models TEXT,
    metadata TEXT,
    created_at TIMESTAMP NOT NULL,
    expires TIMESTAMP,
    -- Budget window columns (LiteLLM stores the real budget here)
    budget_duration VARCHAR(20),
    budget_id VARCHAR(255),
    budget_limits JSONB,
    budget_reset_at TIMESTAMP,
    model_max_budget JSONB,
    soft_budget_cooldown BOOLEAN
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_spend_logs_user ON "LiteLLM_SpendLogs"("user");
CREATE INDEX IF NOT EXISTS idx_spend_logs_api_key ON "LiteLLM_SpendLogs"(api_key);
CREATE INDEX IF NOT EXISTS idx_spend_logs_starttime ON "LiteLLM_SpendLogs"("startTime");
CREATE INDEX IF NOT EXISTS idx_spend_logs_model ON "LiteLLM_SpendLogs"(model);
CREATE INDEX IF NOT EXISTS idx_verification_tokens_user_id ON "LiteLLM_VerificationToken"(user_id);

-- Insert sample data for testing
-- Note: tokens are SHA-256 hashes of the actual API keys
-- sk-test-key-12345 -> 9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b
-- sk-test-key-67890 -> 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b
-- The first key uses a budget_limits window (30d, max 100), the second a flat max_budget.
INSERT INTO "LiteLLM_VerificationToken" (token, key_alias, spend, max_budget, user_id, metadata, created_at, budget_limits, budget_duration, budget_reset_at)
VALUES
    ('9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b', 'test-key', 0.0, NULL, 'test-user-1', '{"email": "test@example.com"}', NOW(), '[{"reset_at": "2026-08-01T00:00:00+00:00", "max_budget": 100.0, "budget_duration": "30d"}]'::jsonb, '30d', '2026-08-01 00:00:00'),
    ('1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b', 'test-key-2', 0.0, 50.0, 'test-user-2', '{"email": "user2@example.com"}', NOW(), NULL, NULL, NULL)
ON CONFLICT (token) DO NOTHING;

-- Insert sample spend logs
-- Note: api_key field also stores hashed keys
INSERT INTO "LiteLLM_SpendLogs" (request_id, api_key, "user", model, spend, total_tokens, prompt_tokens, completion_tokens, "startTime", "endTime")
VALUES
    ('req-001', '9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b', 'test-user-1', 'gpt-4', 0.05, 1000, 800, 200, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '5 seconds'),
    ('req-002', '9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b', 'test-user-1', 'gpt-4', 0.08, 1500, 1200, 300, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '5 seconds'),
    ('req-003', '9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b', 'test-user-1', 'claude-3', 0.03, 800, 600, 200, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '5 seconds'),
    ('req-004', '9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b', 'test-user-1', 'gpt-4', 0.12, 2000, 1600, 400, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '5 seconds'),
    ('req-005', '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b', 'test-user-2', 'gpt-3.5-turbo', 0.01, 500, 400, 100, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '5 seconds')
ON CONFLICT (request_id) DO NOTHING;
