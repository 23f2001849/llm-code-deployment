# ⚡ Quick Reference Guide

## 🚨 First Time Setup (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials (CRITICAL!)
# Edit .env with your NEW tokens (rotate exposed ones!)
nano .env

# 3. Create directories
mkdir -p logs attachments

# 4. Verify everything works
python verify_deployment.py
```

---

## 🎯 Daily Commands

### Start the Server
```bash
python run.py
```
**Keep this running in Terminal 1**

### Test Deployment
```bash
python test_deployment.py
```

### Monitor Logs (real-time)
```bash
tail -f logs/deployment_$(date +%Y%m%d).log
```

---

## 🔧 Debugging Commands

```bash
# Full system check
python verify_deployment.py

# Debug API issues
python debug_api.py

# Test OpenAI connection
python test_openai_detailed.py

# View all logs
ls -lh logs/

# Search logs for errors
grep -i error logs/*.log

# Check server is running
curl http://localhost:8000/health
```

---

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Deploy App (Round 1)
```bash
curl http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "secret": "student_secret_123",
    "task": "unique-task-id",
    "round": 1,
    "nonce": "unique-nonce",
    "brief": "Create a calculator",
    "checks": ["Has MIT license", "README exists"],
    "evaluation_url": "https://example.com/eval",
    "attachments": []
  }'
```

### Update App (Round 2+)
```bash
curl http://localhost:8000/update \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "secret": "student_secret_123",
    "task": "same-task-id",
    "round": 2,
    "nonce": "new-nonce",
    "brief": "Add subtraction feature",
    "checks": ["Calculator has subtract"],
    "evaluation_url": "https://example.com/eval",
    "attachments": []
  }'
```

---

## 🐛 Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Invalid secret" | Check `ALLOWED_SECRETS` in `.env` |
| "Cannot connect" | Start server: `python run.py` |
| "GitHub auth failed" | Regenerate token with `repo` + `workflow` scopes |
| "OpenAI error" | Check API key and credits |
| "Port in use" | Change `API_PORT` in `.env` or kill process |
| "Pages not deploying" | Wait 2-3 minutes, check repo Settings → Pages |

---

## 📊 Monitoring

### Check GitHub Repos
```bash
# List your repos
gh repo list  # If you have GitHub CLI

# Or visit: https://github.com/23f2001849?tab=repositories
```

### Check OpenAI Usage
Visit: https://platform.openai.com/account/usage

### Check Server Status
```bash
# Process status
ps aux | grep "python run.py"

# Port status
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows
```

---

## 🔐 Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] Never committed `.env` to git
- [ ] Rotated exposed credentials
- [ ] GitHub token has minimum scopes (repo, workflow)
- [ ] `ALLOWED_SECRETS` contains unique values
- [ ] Not sharing logs publicly (may contain task details)

---

## 📂 File Reference

| File | Purpose |
|------|---------|
| `.env` | **Credentials** (never commit!) |
| `app.py` | Main FastAPI application |
| `github_client.py` | GitHub operations |
| `llm_generator.py` | OpenAI code generation |
| `evaluation_client.py` | Evaluation submission |
| `run.py` | Server startup |
| `verify_deployment.py` | Full system test |
| `test_deployment.py` | Basic API test |

---

## 🎓 Workflow Steps

1. **Receive Request** → Validate secret
2. **Generate Code** → OpenAI creates app
3. **Create Repo** → Push to GitHub
4. **Enable Pages** → Via REST API (no workflow!)
5. **Submit Evaluation** → POST to evaluation_url
6. **Monitor** → Check logs

---

## 💡 Pro Tips

- Keep server running in background with `nohup` or `screen`
- Use `jq` to format JSON: `curl ... | jq`
- Set up log rotation for production
- Monitor GitHub API rate limits
- Test with httpbin.org before real evaluation
- Keep backups of generated repos

---

## 🆘 Emergency Recovery

```bash
# Server crashed? Restart
python run.py

# Dependencies broken? Reinstall
pip install --force-reinstall -r requirements.txt

# Environment corrupt? Reset
cp .env .env.backup
# Re-edit .env with correct values

# Logs too big? Clear old ones
rm logs/deployment_2024*.log

# Need fresh start?
rm -rf logs/* attachments/*
python verify_deployment.py
```

---

## 📞 Getting Help

1. **Check logs first:** `tail -f logs/deployment_*.log`
2. **Run verification:** `python verify_deployment.py`
3. **Read error messages carefully**
4. **Search error messages online**
5. **Check GitHub/OpenAI status pages**

---

## ✅ Pre-Submission Checklist

```bash
# Quick verification
python verify_deployment.py && echo "✅ READY!" || echo "❌ FIX ISSUES"
```

Should show:
- ✅ File Structure
- ✅ Environment Variables  
- ✅ GitHub Connection
- ✅ OpenAI Connection
- ✅ API Server
- ✅ Deployment Endpoint
- ✅ Security Validation

---

**Keep this reference handy! 📌**