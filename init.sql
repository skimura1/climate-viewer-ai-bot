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

-- Create table for document chunks (used by RAG system)
CREATE TABLE IF NOT EXISTS public.document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(255) UNIQUE NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding vector(1536),
    filename VARCHAR(500) NOT NULL,
    source_file VARCHAR(500),
    relevant INTEGER DEFAULT 1,
    confidence VARCHAR(50),
    relevant_layers TEXT[],
    reasoning TEXT,
    key_findings JSONB,
    locations TEXT[],
    slr_projections TEXT[],
    measurements TEXT[],
    timeframes TEXT[]
);

CREATE INDEX ON document_chunks (chunk_id);
CREATE INDEX ON document_chunks (filename);
CREATE INDEX ON document_chunks (confidence);
CREATE INDEX ON document_chunks USING gin (relevant_layers);
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
