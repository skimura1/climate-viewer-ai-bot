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

-- Create table for climate documentation
CREATE TABLE climate_documentation (
    id SERIAL PRIMARY KEY,
    layer_id VARCHAR(100) NOT NULL,
    chunk_type VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_embedding vector(1536),  -- OpenAI embedding dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX ON climate_documentation 
USING ivfflat (content_embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX ON climate_documentation (layer_id);
CREATE INDEX ON climate_documentation (chunk_type);
