-- LiteLLM Database Additional Setup
-- This script runs after 01-init-databases.sql
-- Ensures proper permissions and prepares database for LiteLLM schema

-- Connect to litellm database
\c litellm;

-- Grant all necessary privileges to dcoder user (used by LiteLLM service)
-- LiteLLM uses the dcoder user credentials from DATABASE_URL
GRANT ALL PRIVILEGES ON SCHEMA public TO dcoder;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dcoder;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dcoder;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO dcoder;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO dcoder;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dcoder;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO dcoder;

-- LiteLLM will automatically create its schema on first run
-- Tables include:
--   - LiteLLM_VerificationToken (virtual keys)
--   - LiteLLM_SpendLogs (usage tracking)
--   - LiteLLM_UserTable (user management)
--   - LiteLLM_TeamTable (team/tenant management)
-- No need to create these manually as LiteLLM handles migrations

-- Display database info
SELECT current_database(), current_user;

-- Show granted privileges
\dp
