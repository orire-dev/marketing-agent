# Marketing Agent - Server Status

## ✅ Server is Running

**Status**: Active on http://localhost:8000

**Process**: Running in background
**Logs**: `/tmp/marketing_agent.log`

## Quick Commands

```bash
# Check if running
curl http://localhost:8000/

# Generate creative
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d @example_request.json

# View logs
tail -f /tmp/marketing_agent.log

# Stop server
pkill -f "uvicorn app.main:app"

# Restart server
cd ~/marketing-agent
source .venv/bin/activate
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/.env | cut -d'=' -f2 | tr -d ' ')
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/marketing_agent.log 2>&1 &
```

## Note on Claude Model

The system is configured to use Claude models. If you see 404 errors, the model name may need updating. The system will fall back to generating basic options if Claude API calls fail.

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.
