# Quick Start: Deploy API for GitHub Pages

## 🚀 Fastest Option: Render.com (Recommended)

### Step 1: Deploy to Render (5 minutes)

1. **Go to**: https://render.com
2. **Sign up** (free account)
3. **Click**: "New +" → "Web Service"
4. **Connect** your GitHub repository: `orire-dev/marketing-agent`
5. **Configure**:
   - **Name**: `marketing-agent-api` (or any name)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Add Environment Variables**:
   - Click "Advanced" → "Add Environment Variable"
   - `ANTHROPIC_API_KEY`: Your Anthropic key
   - `OPENAI_API_KEY`: Your OpenAI key
7. **Click**: "Create Web Service"
8. **Wait** for deployment (2-3 minutes)
9. **Copy** your service URL (e.g., `https://marketing-agent-api.onrender.com`)

### Step 2: Update GitHub Pages UI

1. **Go to**: https://orire-dev.github.io/marketing-agent/
2. **Paste** your Render URL in the "API endpoint" field
3. **Enter** your OpenAI API key (optional)
4. **Generate** creatives! 🎨

---

## 🔧 Alternative: Railway.app (Also Free)

1. **Go to**: https://railway.app
2. **Sign up** with GitHub
3. **New Project** → "Deploy from GitHub repo"
4. **Select**: `orire-dev/marketing-agent`
5. **Railway auto-detects** FastAPI
6. **Add environment variables**:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
7. **Deploy** → Get your URL
8. **Update** GitHub Pages UI with Railway URL

---

## 🧪 Quick Testing: ngrok (Temporary)

If you want to test quickly without deploying:

```bash
# Install ngrok
brew install ngrok  # macOS
# Or download from https://ngrok.com/download

# Start your local server (in another terminal)
cd ~/marketing-agent
source .venv/bin/activate
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/.env | cut -d'=' -f2 | tr -d ' ')
export OPENAI_API_KEY=$(grep OPENAI_API_KEY ~/.env | tail -1 | cut -d'=' -f2 | tr -d ' ')
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal, create tunnel
ngrok http 8000

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
# Paste it in GitHub Pages UI
```

**Note**: ngrok URLs change each restart. Use Render/Railway for permanent solution.

---

## ✅ After Deployment

1. Your API will be live at: `https://your-service.onrender.com` (or similar)
2. GitHub Pages UI: https://orire-dev.github.io/marketing-agent/
3. Enter your API URL in the GitHub Pages UI
4. Generate images! 🎉

---

## 🆘 Troubleshooting

- **CORS errors**: Already configured in the API
- **API not responding**: Check Render/Railway logs
- **Image generation fails**: Check OpenAI API key is set correctly
- **Slow responses**: Free tiers may have cold starts (30-60s first request)
