# Marketing Agent UI Guide

## 🎨 Web Interface Available

A simple, modern web UI has been created for the Marketing Agent!

## Access the UI

**Open in your browser:**
```
http://localhost:8000/
```

The UI provides:
- ✅ Clean, modern interface
- ✅ Form to input generation parameters
- ✅ Real-time generation with loading indicator
- ✅ Beautiful display of results
- ✅ Copy variants per language
- ✅ Design specifications
- ✅ Compliance status
- ✅ Scoring metrics
- ✅ Image generation prompts

## Features

### Input Form
- Product scope (e.g., crypto, stocks)
- Channel selection (social, email, display, video)
- Asset format (1x1, 4x5, 9x16, 16:9)
- Language selection (multi-select)
- Style guidance
- Number of options (1-6)

### Results Display
- Option cards with concept names
- Compliance badges (pass/warning/fail)
- Score badges (brand fit, clarity, conversion, compliance, novelty)
- Copy variants organized by language
- Expandable design specs and prompts
- Error handling with clear messages

## API Endpoints

- `GET /` - Serves the UI
- `GET /health` - Health check (JSON)
- `POST /generate` - Generate creatives (used by UI)
- `GET /docs` - Interactive API documentation

## Troubleshooting

If the UI doesn't load:
1. Check server is running: `curl http://localhost:8000/health`
2. Check logs: `tail -f /tmp/marketing_agent.log`
3. Restart server if needed

The UI calls the same `/generate` endpoint that the API uses, so all functionality is available through the web interface.
