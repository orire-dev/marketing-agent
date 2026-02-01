# Deployment Guide for GitHub Pages + API

## Option 1: Quick Testing with ngrok (Temporary)

### Step 1: Install ngrok
```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

### Step 2: Start your local server
```bash
cd ~/marketing-agent
source .venv/bin/activate
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/.env | cut -d'=' -f2 | tr -d ' ')
export OPENAI_API_KEY=$(grep OPENAI_API_KEY ~/.env | tail -1 | cut -d'=' -f2 | tr -d ' ')
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 3: Create ngrok tunnel
```bash
ngrok http 8000
```

### Step 4: Update GitHub Pages UI
Copy the ngrok URL (e.g., `https://abc123.ngrok.io`) and update the API URL in the GitHub Pages UI.

**Note:** ngrok URLs change each time you restart, so this is only for testing.

---

## Option 2: Production Deployment (Recommended)

### Deploy API to Render.com (Free tier available)

1. **Create account**: https://render.com

2. **Create new Web Service**:
   - Connect your GitHub repository
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment variables:
     - `ANTHROPIC_API_KEY`: Your Anthropic key
     - `OPENAI_API_KEY`: Your OpenAI key

3. **Get your Render URL**: e.g., `https://marketing-agent.onrender.com`

4. **Update GitHub Pages UI** to use your Render URL

### Deploy API to Railway.app (Free tier available)

1. **Create account**: https://railway.app

2. **New Project** → Deploy from GitHub

3. **Configure**:
   - Add environment variables
   - Railway auto-detects FastAPI

4. **Get your Railway URL**: e.g., `https://marketing-agent-production.up.railway.app`

5. **Update GitHub Pages UI** to use your Railway URL

### Deploy API to Fly.io (Free tier available)

1. **Install flyctl**: https://fly.io/docs/getting-started/installing-flyctl/

2. **Create app**:
   ```bash
   cd ~/marketing-agent
   fly launch
   ```

3. **Set secrets**:
   ```bash
   fly secrets set ANTHROPIC_API_KEY=your_key
   fly secrets set OPENAI_API_KEY=your_key
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

5. **Get your Fly.io URL**: e.g., `https://marketing-agent.fly.dev`

---

## Option 3: Update GitHub Pages Default API URL

After deploying, we can update the default API URL in the GitHub Pages UI to point to your deployed server.
