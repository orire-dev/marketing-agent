# Step-by-Step: Deploy to Render.com

## 🚀 Quick Deployment Guide (5 minutes)

### Step 1: Create Render Account
1. Go to: **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with GitHub (recommended) or email

### Step 2: Create New Web Service
1. Once logged in, click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect account"** next to GitHub (if not already connected)
4. Authorize Render to access your GitHub repositories

### Step 3: Select Your Repository
1. In the repository list, find: **`orire-dev/marketing-agent`**
2. Click **"Connect"** next to it

### Step 4: Configure the Service
Fill in these settings:

**Basic Settings:**
- **Name**: `marketing-agent-api` (or any name you like)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: Leave empty (or `./` if required)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- Click **"Advanced"** to expand
- **Auto-Deploy**: `Yes` (deploys on every push to main)

### Step 5: Add Environment Variables
Click **"Add Environment Variable"** and add these:

1. **ANTHROPIC_API_KEY**
   - Value: `YOUR_ANTHROPIC_API_KEY` (get from ~/.env or your Anthropic account)

2. **OPENAI_API_KEY**
   - Value: `YOUR_OPENAI_API_KEY` (get from ~/.env or your OpenAI account)

### Step 6: Deploy
1. Click **"Create Web Service"**
2. Wait 2-3 minutes for deployment
3. Watch the build logs - it will show progress

### Step 7: Get Your URL
Once deployment is complete:
1. You'll see a URL like: `https://marketing-agent-api.onrender.com`
2. **Copy this URL** - this is your API endpoint!

### Step 8: Test Your Deployment
1. Open: `https://your-service-name.onrender.com/health`
2. You should see: `{"service":"eToro Marketing Agent","status":"running","version":"0.1.0"}`

### Step 9: Use in GitHub Pages
1. Go to: **https://orire-dev.github.io/marketing-agent/**
2. In "API Configuration":
   - **API endpoint**: Paste your Render URL (e.g., `https://marketing-agent-api.onrender.com`)
   - **OpenAI API key**: Leave empty (it will use the server's env var)
3. Generate creatives! 🎨

---

## ⚠️ Important Notes

- **Free Tier**: Render free tier may spin down after 15 minutes of inactivity
- **Cold Start**: First request after inactivity may take 30-60 seconds
- **Environment Variables**: Keep your keys secure - never commit them to GitHub
- **Auto-Deploy**: Every push to `main` will automatically redeploy

---

## 🔧 Troubleshooting

**Build fails?**
- Check build logs in Render dashboard
- Ensure `requirements.txt` has all dependencies
- Verify Python version (should be 3.11+)

**Service won't start?**
- Check start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Verify environment variables are set
- Check logs for error messages

**404 errors?**
- Make sure you're using the full URL: `https://your-service.onrender.com/generate`
- Check that the service is "Live" (not "Sleeping")

---

## 📞 Need Help?

If you encounter issues:
1. Check Render logs (in dashboard)
2. Verify environment variables are set correctly
3. Test the `/health` endpoint first
4. Make sure the service is not "Sleeping" (click to wake it up)
