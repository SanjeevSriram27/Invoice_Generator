-- Fix PostgreSQL schema permissions for invoice_user
-- Run this with: psql -U postgres -d invoice_generator -f fix_permissions.sql

-- Connect to the database
\c invoice_generator

-- Grant all privileges on schema public to invoice_user
GRANT ALL ON SCHEMA public TO invoice_user;

-- Grant all privileges on all existing tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO invoice_user;

-- Grant all privileges on all existing sequences
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO invoice_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO invoice_user;

-- Set default privileges for future sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO invoice_user;

-- For PostgreSQL 15+, also grant USAGE on schema
GRANT USAGE ON SCHEMA public TO invoice_user;
GRANT CREATE ON SCHEMA public TO invoice_user;

-- Verify permissions
SELECT
    grantee,
    privilege_type
FROM
    information_schema.role_table_grants
WHERE
    grantee = 'invoice_user';

SELECT 'Permissions granted successfully!' as status;
