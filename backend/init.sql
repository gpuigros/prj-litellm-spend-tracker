-- Initialize LiteLLM database schema for testing
-- This simulates the tables that LiteLLM creates

-- Spend logs table
CREATE TABLE IF NOT EXISTS litellm_spend_logs (
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

-- Virtual keys table
CREATE TABLE IF NOT EXISTS litellm_verification_tokens (
    token VARCHAR(255) PRIMARY KEY,
    key_alias VARCHAR(255),
    spend FLOAT NOT NULL DEFAULT 0.0,
    max_budget FLOAT,
    user_id VARCHAR(255),
    team_id VARCHAR(255),
    models TEXT,
    metadata TEXT,
    created_at TIMESTAMP NOT NULL,
    expires TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_spend_logs_user ON litellm_spend_logs("user");
CREATE INDEX IF NOT EXISTS idx_spend_logs_api_key ON litellm_spend_logs(api_key);
CREATE INDEX IF NOT EXISTS idx_spend_logs_starttime ON litellm_spend_logs("startTime");
CREATE INDEX IF NOT EXISTS idx_spend_logs_model ON litellm_spend_logs(model);
CREATE INDEX IF NOT EXISTS idx_verification_tokens_user_id ON litellm_verification_tokens(user_id);

-- Insert sample data for testing
INSERT INTO litellm_verification_tokens (token, key_alias, spend, max_budget, user_id, metadata, created_at)
VALUES 
    ('sk-test-key-12345', 'test-key', 0.0, 100.0, 'test-user-1', '{"email": "test@example.com"}', NOW()),
    ('sk-test-key-67890', 'test-key-2', 0.0, 50.0, 'test-user-2', '{"email": "user2@example.com"}', NOW())
ON CONFLICT (token) DO NOTHING;

-- Insert sample spend logs
INSERT INTO litellm_spend_logs (request_id, api_key, "user", model, spend, total_tokens, prompt_tokens, completion_tokens, "startTime", "endTime")
VALUES
    ('req-001', 'sk-test-key-12345', 'test-user-1', 'gpt-4', 0.05, 1000, 800, 200, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '5 seconds'),
    ('req-002', 'sk-test-key-12345', 'test-user-1', 'gpt-4', 0.08, 1500, 1200, 300, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '5 seconds'),
    ('req-003', 'sk-test-key-12345', 'test-user-1', 'claude-3', 0.03, 800, 600, 200, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '5 seconds'),
    ('req-004', 'sk-test-key-12345', 'test-user-1', 'gpt-4', 0.12, 2000, 1600, 400, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '5 seconds'),
    ('req-005', 'sk-test-key-67890', 'test-user-2', 'gpt-3.5-turbo', 0.01, 500, 400, 100, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '5 seconds')
ON CONFLICT (request_id) DO NOTHING;
