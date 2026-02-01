# Marketing Agent Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd ~/marketing-agent
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Or if using pip:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Create Databricks Tables

```bash
# Connect to Databricks and run:
databricks sql execute -f databricks/sql/create_tables.sql -p orire@etoro.com
```

### 4. Ingest Brand Materials (Optional)

```bash
python -m ingest.ingest_brand \
  --brandbook fixtures/sample_brand_voice.txt \
  --tone fixtures/sample_brand_voice.txt \
  --valueprop fixtures/sample_brand_voice.txt
```

### 5. Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Test the API

```bash
# In another terminal
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d @example_request.json | jq '.'
```

## Project Structure

```
marketing-agent/
├── app/                    # FastAPI application
│   ├── main.py            # API endpoints
│   ├── schemas.py         # Pydantic models
│   ├── llm_client.py      # Claude client
│   ├── rag.py             # Retrieval (RAG)
│   ├── planner.py         # Planning agent
│   ├── generator.py       # Copy generation
│   ├── compliance.py      # Compliance checking
│   ├── prompt_builder.py  # Image/motion prompts
│   ├── ranker.py          # Option ranking
│   └── renderers/         # Image/GIF renderers
├── ingest/                # Document ingestion
├── databricks/            # Databricks notebooks & SQL
├── fixtures/              # Sample data
├── tests/                 # Unit tests
└── example_request.json   # Example API request
```

## Next Steps

1. **Integrate Databricks Vector Search** - Replace stub RAG with real vector search
2. **Add real document ingestion** - Connect to Databricks tables
3. **Implement renderer** - Add actual image generation (DALL-E, Midjourney, etc.)
4. **Add persistence** - Store generations in Databricks
5. **Build UI** - Create Next.js frontend for CMO

## API Endpoints

- `POST /generate` - Generate creative options
- `GET /generation/{id}` - Get previous generation (TODO)
- `POST /regenerate` - Regenerate with constraints (TODO)

## Example Request

See `example_request.json` for a complete example.

## Example Output

See `example_output.json` for expected response format.
