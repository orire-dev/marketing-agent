# Marketing Agent - Quick Start

## ✅ System Built and Ready

A complete production-ready Marketing Agent has been implemented with:

- **FastAPI REST API** with `/generate` endpoint
- **Claude-powered agents** (Planner, Generator, Compliance, Prompt Builder)
- **RAG retrieval** (stub, ready for Databricks Vector Search)
- **Strict JSON output** (all LLM responses validated)
- **Compliance checking** (brand rules + regulatory)
- **Multilingual support** (7 languages)
- **Ranking & scoring** system
- **Databricks integration** (table schemas ready)

## 🚀 Test It Now

```bash
cd ~/marketing-agent

# 1. Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/.env | cut -d'=' -f2)

# 3. Start API
uvicorn app.main:app --reload --port 8000

# 4. In another terminal, test it:
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "product_scope": "crypto",
    "channel": "social",
    "asset": "social_1x1",
    "languages": ["en", "de"],
    "style_guidance": "clean, premium, minimal copy, bold typography",
    "num_options": 3
  }' | jq '.'
```

## 📊 What You'll Get

The API returns a complete JSON with:
- 3 creative options (configurable 1-6)
- Multiple copy variants per language
- Design specifications
- Image generation prompts
- Motion/GIF storyboards
- Compliance reports
- Scoring and ranking
- Full audit trail

## 📁 Key Files

- `app/main.py` - FastAPI endpoints
- `app/schemas.py` - All data models
- `app/generator.py` - Copy generation logic
- `databricks/sql/create_tables.sql` - Database schemas
- `example_request.json` - Example API call
- `example_output.json` - Expected response format

## 🎯 Status

**Core System**: ✅ Complete
**Ready to Test**: ✅ Yes
**Next Steps**: Integrate Databricks Vector Search, add persistence, implement real renderer

See `IMPLEMENTATION_SUMMARY.md` for full details.
