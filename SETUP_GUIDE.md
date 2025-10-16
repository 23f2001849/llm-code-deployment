# 🚀 LLM Code Deployment System - Complete Setup Guide

## 🔐 Step 1: Secure Your Credentials (CRITICAL!)

### ⚠️ Security Alert
Your `.env` file currently contains **REAL credentials that are exposed**. You MUST:

1. **Revoke your GitHub token immediately:**
   - Go to https://github.com/settings/tokens
   - Find the token `ghp_M96GptjqzyWL...`
   - Click "Delete" or "Revoke"

2. **Rotate your OpenAI API key:**
   - Go to https://platform.openai.com/api-keys
   - Delete the exposed key `sk-proj-n1SB-mjufo...`
   - Create a new key

3. **Create new credentials:**
   ```bash
   # GitHub Personal Access Token
   # Go to: https://github.com/settings/tokens/new
   # Name: LLM-Deployment-Token
   # Scopes needed: repo, workflow
   
   # OpenAI API Key  
   # Go to: https://platform.openai.com/api-keys
   # Create new secret key
   ```

4. **Update your .env file** with the NEW credentials:
   ```env
   GITHUB_TOKEN=ghp_YOUR_NEW_TOKEN_HERE
   GITHUB_USERNAME=23f2001849
   OPENAI_API_KEY=sk-YOUR_NEW_KEY_HERE
   ALLOWED_SECRETS=student_secret_123,test_secret_456
   ```

5. **Never commit .env to git:**
   ```bash
   # Make sure .env is in .gitignore
   echo ".env" >> .gitignore
   git rm --cached .env  # Remove if already committed
   ```

---

## 📋 Step 2: Prerequisites

### Required Software
- **Python 3.8+** (check: `python --version`)
- **pip** (check: `pip --version`)
- **Git** (check: `git --version`)
- **GitHub Account** with Personal Access Token
- **OpenAI Account** with API access

### System Requirements
- Internet connection
- 1GB free disk space
- Port 8000 available

---

## 🛠️ Step 3: Installation

### 1. Clone or Download Project
```bash
cd your-project-directory
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

### 3. Create Required Directories
```bash
mkdir -p logs attachments
```

### 4. Configure Environment
```bash
# Copy example if needed
cp .env.example .env  # if you have an example file

# Edit .env with your credentials
nano .env  # or use any text editor
```

---

## ✅ Step 4: Verification

### Run the Verification Script
```bash
python verify_deployment.py
```

This will test:
- ✅ Environment variables
- ✅ GitHub API connection
- ✅ OpenAI API connection
- ✅ File structure
- ✅ API server (if running)
- ✅ Security validation

**Expected Output:**
```
============================================================
          LLM CODE DEPLOYMENT SYSTEM - VERIFICATION
============================================================

TEST 1: Environment Variables
✓ GITHUB_TOKEN is set
✓ GITHUB_USERNAME is set
✓ OPENAI_API_KEY is set
✓ ALLOWED_SECRETS is set

TEST 2: GitHub API Connection
✓ Connected to GitHub as: 23f2001849
...

🎉 ALL TESTS PASSED! (7/7)
```

---

## 🚀 Step 5: Start the Server

### Terminal 1: Run the API Server
```bash
python run.py
```

**Expected Output:**
```
🚀 Starting LLM Code Deployment API
📡 Server: 127.0.0.1:8000
🔧 Debug: True
📚 API Docs: http://localhost:8000/docs

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal running!**

### Terminal 2: Test the Deployment
```bash
python test_deployment.py
```

**Expected Output:**
```
🚀 Starting LLM Code Deployment API Tests
==================================================

🧪 Health Check
✅ Health Check: PASSED

🧪 Root Endpoint
✅ Root Endpoint: PASSED

🧪 Invalid Secret
✅ Invalid Secret: PASSED

🧪 Deployment
Deployment started successfully!
✅ Deployment: PASSED

📊 Test Results Summary:
Overall: 4/4 tests passed
🎉 All tests passed! The API is working correctly.
```

---

## 📊 Step 6: Monitor Deployment

### Check Logs
```bash
# View today's log file
tail -f logs/deployment_$(date +%Y%m%d).log

# Search for specific task
grep "task-name" logs/deployment_*.log
```

### Check API Docs
Open in browser: http://localhost:8000/docs

This shows:
- All available endpoints
- Request/response schemas
- Try out API calls directly

---

## 🧪 Step 7: Full End-to-End Test

### Create a Test Request
```bash
curl http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "student_secret_123",
    "task": "test-app-001",
    "round": 1,
    "nonce": "test-nonce-001",
    "brief": "Create a simple calculator web app",
    "checks": [
      "Repo has MIT license",
      "README.md is professional",
      "Calculator has add/subtract functions"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'
```

### What Happens Next?

1. **API receives request** (instant)
   - Validates secret
   - Returns 200 response
   - Starts background processing

2. **LLM generates code** (30-60 seconds)
   - Creates index.html
   - Creates README.md
   - Adds LICENSE

3. **GitHub operations** (10-30 seconds)
   - Creates new repository
   - Commits files
   - Enables GitHub Pages

4. **Evaluation submission** (5-10 seconds)
   - POSTs to evaluation_url
   - Retries on failure

5. **Total time:** ~60-120 seconds

### Verify Deployment

```bash
# Check your GitHub account
# You should see a new repo: llm-app-{hash}-{hash}-{timestamp}

# Visit GitHub Pages URL
# https://23f2001849.github.io/llm-app-{hash}-{hash}-{timestamp}/
```

---

## 🔧 Troubleshooting

### Issue 1: "GITHUB_TOKEN environment variable is required"
**Solution:** Edit `.env` and add your GitHub token

### Issue 2: "Failed to create repository: Bad credentials"
**Solution:** 
- Check token is valid: https://github.com/settings/tokens
- Verify token has `repo` and `workflow` scopes
- Regenerate token if needed

### Issue 3: "OpenAI connection failed"
**Solution:**
- Verify API key at: https://platform.openai.com/api-keys
- Check you have credits: https://platform.openai.com/account/usage
- Test with: `python test_openai_detailed.py`

### Issue 4: "Cannot connect to API server"
**Solution:**
- Make sure `python run.py` is running in another terminal
- Check port 8000 is not used: `lsof -i :8000` (Mac/Linux)
- Try different port in `.env`: `API_PORT=8001`

### Issue 5: "GitHub Pages not deploying"
**Solution:**
- Check repo exists on GitHub
- Verify Pages is enabled: Repo Settings → Pages
- Wait 2-3 minutes for Pages to build
- Check for errors in repo's Actions tab

### Issue 6: "All checks have failed" in GitHub Actions
**Solution:**
- This is the original issue mentioned
- The updated `github_client.py` fixes this by using REST API
- No workflow is created, avoiding the failure
- Pages are enabled directly via API

### Issue 7: Rate Limit Errors
**Solution:**
- GitHub: Wait 1 hour or use authenticated requests
- OpenAI: Check usage limits and billing

---

## 📁 Project Structure

```
llm-code-deployment/
├── .env                    # Your credentials (NEVER commit!)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── README.md             # Project overview
├── SETUP_GUIDE.md        # This file
│
├── config.py             # Configuration loader
├── app.py                # FastAPI application
├── run.py                # Server startup script
│
├── github_client.py      # GitHub API operations
├── llm_generator.py      # OpenAI code generation
├── evaluation_client.py  # Evaluation submission
├── utils.py              # Helper functions
│
├── test_deployment.py    # Basic tests
├── verify_deployment.py  # Comprehensive verification
├── debug_api.py          # Debugging utilities
│
├── logs/                 # Deployment logs
│   └── deployment_YYYYMMDD.log
│
└── attachments/          # Temporary file storage
```

---

## 🎯 Next Steps

1. **Run verification:** `python verify_deployment.py`
2. **Start server:** `python run.py`
3. **Test deployment:** `python test_deployment.py`
4. **Submit to course:**
   - Fill Google Form with:
     - API endpoint: `http://your-ip:8000`
     - Secret: `student_secret_123`
     - GitHub username: `23f2001849`
5. **Monitor logs:** `tail -f logs/deployment_*.log`

---

## 📞 Support

### Debug Commands
```bash
# Check environment
python debug_api.py

# Test OpenAI
python test_openai_detailed.py

# View logs
ls -lh logs/
cat logs/deployment_*.log

# Check running processes
ps aux | grep python
```

### Common Fixes
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Clear logs
rm logs/*.log

# Clear attachments
rm attachments/*

# Restart server
# Press Ctrl+C in server terminal
python run.py
```

---

## ✅ Pre-Submission Checklist

- [ ] All tests pass in `verify_deployment.py`
- [ ] Server runs without errors
- [ ] Test deployment creates GitHub repo successfully
- [ ] GitHub Pages URL is accessible
- [ ] Evaluation POST succeeds
- [ ] Logs show no errors
- [ ] `.env` is in `.gitignore`
- [ ] Real credentials are secured (not exposed)

---

## 🎓 Understanding the Workflow

```
Student → Google Form → Course Server
                            ↓
                    POST /deploy (JSON)
                            ↓
                    Your API Server
                            ↓
            ┌───────────────┴──────────────┐
            ↓                              ↓
    LLM Generates Code              Validates Request
            ↓                              ↓
    Creates Files              Saves Attachments
            ↓                              ↓
    GitHub Operations          Background Processing
            ↓                              ↓
    Creates Repo               Enables Pages
            ↓                              ↓
    Commits Files              Gets Commit SHA
            ↓                              ↓
            └───────────────┬──────────────┘
                            ↓
                    POST to evaluation_url
                            ↓
                    Course Evaluation System
                            ↓
                    Tests & Scores Your App
```

---

**Good luck with your deployment! 🚀**