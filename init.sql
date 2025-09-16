-- Initialize climate viewer database
-- This file will be executed when the PostgreSQL container starts

-- Create any initial tables or data here if needed
-- Example:
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     username VARCHAR(50) UNIQUE NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE climate_viewer_dev TO dev_user;

-- Connect to your existing PostgreSQL database (where PostGIS is)
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for chunks (used by RAG system)
CREATE TABLE IF NOT EXISTS public.chunks (
    id SERIAL PRIMARY KEY,
    layer_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX ON chunks 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX ON chunks (layer_id);
