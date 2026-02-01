# eToro Marketing Agent - One-Click Social Ad Generator

Production-ready AI agent for generating marketing messaging and creative directions aligned to brand book and segmentation.

## 🚀 Features

- **Multi-option generation**: Generate 3-5 distinct creative options per request
- **Platform support**: X (Twitter), Facebook, Email, Display
- **Format support**: Static images, Motion ads, Short videos
- **Multi-language**: EN, DE, ES, FR, IT, AR, HE
- **Image generation**: DALL-E 3 integration for actual image creation
- **Brand compliance**: Automatic brand alignment and regulatory compliance
- **Real-time generation**: Get results in under 60 seconds

## 📋 Requirements

- Python 3.11+
- Anthropic API key (for Claude)
- OpenAI API key (for DALL-E 3 image generation)

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd marketing-agent
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Configure API Keys

Add to `~/.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
```

### 3. Run the Server

```bash
source .venv/bin/activate
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/.env | cut -d'=' -f2 | tr -d ' ')
export OPENAI_API_KEY=$(grep OPENAI_API_KEY ~/.env | tail -1 | cut -d'=' -f2 | tr -d ' ')
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Access the UI

Open http://localhost:8000/ in your browser

## 📖 API Documentation

Interactive API docs: http://localhost:8000/docs

### Generate Creative

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "product_scope": "crypto",
    "channel": "social",
    "asset": "social_1x1",
    "languages": ["en", "de"],
    "style_guidance": "clean, premium, minimal copy, bold typography",
    "num_options": 3
  }'
```

## 🏗️ Architecture

- **FastAPI**: REST API server
- **Claude (Anthropic)**: Copy generation and creative direction
- **DALL-E 3 (OpenAI)**: Image generation
- **Databricks**: Data storage and RAG (Vector Search)
- **Pydantic**: Type-safe schemas

## 📁 Project Structure

```
marketing-agent/
├── app/              # FastAPI application
│   ├── main.py      # API endpoints
│   ├── schemas.py   # Data models
│   ├── generator.py # Copy generation
│   └── renderers/   # Image generation
├── static/          # Web UI
├── databricks/      # Databricks integration
└── tests/           # Unit tests
```

## 🐛 Troubleshooting

### Image Generation Fails

If you see "billing limit reached":
1. Check OpenAI billing: https://platform.openai.com/account/billing
2. Add credits or increase limits
3. The system will still generate copy and prompts

### Claude API Errors

- Verify `ANTHROPIC_API_KEY` is set correctly
- Check model availability (using `claude-3-haiku-20240307`)

## 📝 License

Internal eToro project

## 👥 Contributors

eToro Marketing & GenAI Team
