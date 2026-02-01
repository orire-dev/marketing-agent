-- Marketing Agent Databricks Tables
-- Unity Catalog: main.marketing_agent

-- Brand assets (chunks from brand book, tone guide, value prop)
CREATE TABLE IF NOT EXISTS main.marketing_agent.brand_assets (
    chunk_id STRING NOT NULL,
    doc_name STRING NOT NULL,
    doc_type STRING NOT NULL,  -- 'brand_book', 'tone_guide', 'value_prop'
    section STRING,
    page_number INT,
    chunk_text STRING NOT NULL,
    chunk_index INT,
    metadata MAP<STRING, STRING>,
    embedding ARRAY<FLOAT>,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
) USING DELTA
CLUSTER BY (doc_type, doc_name);

-- Product catalog (features, instruments, restrictions, disclaimers)
CREATE TABLE IF NOT EXISTS main.marketing_agent.product_catalog (
    product_id STRING NOT NULL,
    product_name STRING NOT NULL,
    product_type STRING NOT NULL,  -- 'crypto', 'stocks', 'ETFs', 'CFDs'
    description STRING,
    features ARRAY<STRING>,
    restrictions ARRAY<STRING>,
    required_disclaimers ARRAY<STRING>,
    prohibited_claims ARRAY<STRING>,
    compliance_notes STRING,
    metadata MAP<STRING, STRING>,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
) USING DELTA
CLUSTER BY (product_type);

-- Segments (persona attributes, pains, language preferences)
CREATE TABLE IF NOT EXISTS main.marketing_agent.segments (
    segment_id STRING NOT NULL,
    segment_name STRING NOT NULL,
    persona_attributes MAP<STRING, STRING>,
    jobs_to_be_done ARRAY<STRING>,
    pain_points ARRAY<STRING>,
    objections ARRAY<STRING>,
    language_preferences ARRAY<STRING>,
    tone_preferences MAP<STRING, STRING>,
    metadata MAP<STRING, STRING>,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
) USING DELTA;

-- Creative requests (briefs, metadata, requester)
CREATE TABLE IF NOT EXISTS main.marketing_agent.creative_requests (
    request_id STRING NOT NULL,
    requester STRING,
    product_scope STRING NOT NULL,
    channel STRING NOT NULL,
    asset_format STRING NOT NULL,
    languages ARRAY<STRING> NOT NULL,
    segment_id STRING,
    style_guidance STRING,
    campaign_goal STRING,
    constraints MAP<STRING, STRING>,
    request_metadata MAP<STRING, STRING>,
    created_at TIMESTAMP NOT NULL
) USING DELTA
PARTITIONED BY (date_trunc('day', created_at));

-- Generations (LLM outputs + scoring + compliance results)
CREATE TABLE IF NOT EXISTS main.marketing_agent.generations (
    generation_id STRING NOT NULL,
    request_id STRING NOT NULL,
    option_id STRING NOT NULL,
    concept_name STRING,
    rationale STRING,
    copy_json STRING NOT NULL,  -- JSON string of copy per language
    design_spec_json STRING NOT NULL,  -- JSON string of design spec
    prompts_json STRING NOT NULL,  -- JSON string of prompts
    compliance_status STRING NOT NULL,  -- 'pass', 'warning', 'fail'
    compliance_flags ARRAY<STRING>,
    scores_json STRING NOT NULL,  -- JSON string of scores
    model_version STRING,
    retrieved_sources_json STRING,  -- JSON array of sources
    created_at TIMESTAMP NOT NULL
) USING DELTA
PARTITIONED BY (date_trunc('day', created_at))
CLUSTER BY (request_id, option_id);

-- Creatives (image/gif metadata + storage paths)
CREATE TABLE IF NOT EXISTS main.marketing_agent.creatives (
    creative_id STRING NOT NULL,
    generation_id STRING NOT NULL,
    option_id STRING NOT NULL,
    asset_format STRING NOT NULL,
    language STRING NOT NULL,
    asset_type STRING NOT NULL,  -- 'image', 'gif', 'motion'
    storage_path STRING NOT NULL,
    storage_uri STRING,
    prompt_used STRING,
    seed INT,
    metadata MAP<STRING, STRING>,
    created_at TIMESTAMP NOT NULL
) USING DELTA
PARTITIONED BY (date_trunc('day', created_at))
CLUSTER BY (generation_id, option_id);

-- Vector Search Index (for RAG retrieval)
-- Note: This is created via Databricks Vector Search UI or API
-- Example index config would be stored separately

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_brand_assets_doc_type 
ON main.marketing_agent.brand_assets (doc_type, doc_name);

CREATE INDEX IF NOT EXISTS idx_product_catalog_type 
ON main.marketing_agent.product_catalog (product_type);

CREATE INDEX IF NOT EXISTS idx_generations_request 
ON main.marketing_agent.generations (request_id);

CREATE INDEX IF NOT EXISTS idx_creatives_generation 
ON main.marketing_agent.creatives (generation_id, option_id);
