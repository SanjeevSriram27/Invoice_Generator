-- PostgreSQL Database Setup Script for Invoice Generator
-- Run this with: psql -U postgres -f setup_database.sql

-- Drop database if exists (optional - comment out in production)
-- DROP DATABASE IF EXISTS invoice_generator;
-- DROP USER IF EXISTS invoice_user;

-- Create database
CREATE DATABASE invoice_generator
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Create user
CREATE USER invoice_user WITH PASSWORD 'invoice_pass_2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE invoice_generator TO invoice_user;

-- Connect to the database
\c invoice_generator

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO invoice_user;

-- Grant default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO invoice_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO invoice_user;

-- Display success message
SELECT 'Database invoice_generator created successfully!' as status;
