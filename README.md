# 🚀 LLM Code Deployment System

A complete automated system that builds, deploys, and updates web applications using LLM assistance.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Live API:** [https://Krishna-11Analyst-llm-code-deployment.hf.space](https://Krishna-11Analyst-llm-code-deployment.hf.space)

**API Documentation:** [https://Krishna-11Analyst-llm-code-deployment.hf.space/docs](https://Krishna-11Analyst-llm-code-deployment.hf.space/docs)

---

## ✨ Features

- ✅ **Smart Code Generation:** Uses OpenAI GPT-4 to generate functional web applications
- ✅ **GitHub Integration:** Automatic repository creation and GitHub Pages deployment
- ✅ **Multi-Round Support:** Handle initial deployment (Round 1) and subsequent updates (Round 2+)
- ✅ **GitHub Actions:** Automated CI/CD pipeline for Pages deployment
- ✅ **Evaluation Ready:** Automatic submission to evaluation endpoints with retry logic
- ✅ **Security:** Secret-based authentication and validation
- ✅ **Robust Error Handling:** Comprehensive logging and retry mechanisms
- ✅ **Background Processing:** Non-blocking asynchronous deployment operations
- ✅ **Docker Support:** Containerized deployment for consistency

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Local Testing](#-local-testing)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Usage Examples](#-usage-examples)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Author](#-author)

---

## 🔧 Prerequisites

- **Python 3.8+**
- **GitHub Account** with Personal Access Token
- **OpenAI API Key** with GPT-4 or GPT-3.5 access
- **Git** installed locally
- **Docker** (optional, for containerized deployment)

---

## 📦 Installation

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/23f2001849/llm-code-deployment.git
cd llm-code-deployment

# Run automated setup
python setup_environment.py
```

### Option 2: Manual Setup
```bash
# Clone the repository
git clone https://github.com/23f2001849/llm-code-deployment.git
cd llm-code-deployment

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Edit .env with your credentials
# (See Configuration section below)
```

---

## 🔐 Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `GITHUB_TOKEN` | GitHub Personal Access Token (with `repo` and `workflow` scopes) | `ghp_xxxxxxxxxxxx` | ✅ Yes |
| `GITHUB_USERNAME` | Your GitHub username | `23f2001849` | ✅ Yes |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-xxxxxxxxx` | ✅ Yes |
| `ALLOWED_SECRETS` | Comma-separated authentication secrets | `student_secret_123,test_secret_456` | ✅ Yes |
| `API_HOST` | API host address (use `0.0.0.0` for production) | `0.0.0.0` | ✅ Yes |
| `API_PORT` | API port (use `7860` for Huggingface Spaces) | `7860` | ✅ Yes |
| `DEBUG` | Debug mode (set to `false` in production) | `false` | ✅ Yes |

### Example `.env` File
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=7860
DEBUG=false

# GitHub Configuration
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_USERNAME=23f2001849

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your_openai_key_here

# Security
ALLOWED_SECRETS=student_secret_123,test_secret_456
```

### GitHub Token Permissions

Your GitHub Personal Access Token must have the following scopes:
- ✅ `repo` (Full control of private repositories)
- ✅ `workflow` (Update GitHub Action workflows)

**Generate token at:** [https://github.com/settings/tokens/new](https://github.com/settings/tokens/new)

---

## 📡 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-16T10:00:00.000000",
  "deployment_method": "github_actions",
  "components": {
    "api": "ok",
    "github": "ok",
    "openai": "ok"
  }
}
```

---

### Deploy Application (Round 1)
```http
POST /deploy
```

Creates a new GitHub repository with LLM-generated code and deploys to GitHub Pages.

**Request Body:**
```json
{
  "email": "23f2001849@ds.study.iitm.ac.in",
  "task": "deploy",
  "round": 1,
  "nonce": "unique-request-id",
  "brief": {
    "name": "Portfolio Website",
    "description": "Professional portfolio showcasing projects and skills"
  },
  "checks": ["has_readme", "has_license", "has_actions"],
  "evaluation_url": "https://evaluation-server.com/callback",
  "secret": "student_secret_123"
}
```

**Response (200 OK):**
```json
{
  "status": "processing",
  "message": "Deployment started successfully. The application is being generated and deployed via GitHub Actions.",
  "repo_url": "https://github.com/23f2001849/llm-app-xxxxxx",
  "pages_url": "https://23f2001849.github.io/llm-app-xxxxxx",
  "task_id": "deploy-20251016-xxxxxx",
  "timestamp": "2025-10-16T10:00:00.000000"
}
```

**Process Flow:**
1. Validates request and authenticates secret
2. Generates code using OpenAI GPT-4 (~30 seconds)
3. Creates GitHub repository (~3 seconds)
4. Commits files (index.html, README.md, LICENSE)
5. Sets up GitHub Actions workflow
6. Triggers Pages deployment (~40 seconds)
7. Sends evaluation callback
8. **Total time: ~90 seconds**

---

### Update Application (Round 2+)
```http
POST /update
```

Updates an existing repository with modifications based on new requirements.

**Request Body:**
```json
{
  "email": "23f2001849@ds.study.iitm.ac.in",
  "task": "update",
  "round": 2,
  "nonce": "unique-request-id-2",
  "brief": {
    "name": "Enhanced Portfolio",
    "description": "Updated with animations, contact form, and responsive design"
  },
  "checks": ["has_readme", "has_license", "responsive_design"],
  "evaluation_url": "https://evaluation-server.com/callback",
  "secret": "student_secret_123"
}
```

**Response:** Same structure as `/deploy` endpoint

---

### Check Deployment Status
```http
GET /status/{task_id}
```

**Response:**
```json
{
  "task_id": "deploy-20251016-xxxxxx",
  "status": "completed",
  "repo_url": "https://github.com/23f2001849/llm-app-xxxxxx",
  "pages_url": "https://23f2001849.github.io/llm-app-xxxxxx",
  "created_at": "2025-10-16T10:00:00.000000",
  "completed_at": "2025-10-16T10:01:30.000000"
}
```

---

## 🧪 Local Testing

### Run with Python
```bash
# Make sure virtual environment is activated
python run.py

# API will be available at:
# http://localhost:7860
```

### Run with Docker
```bash
# Build Docker image
docker build -t llm-deployment .

# Run container
docker run -p 7860:7860 --env-file .env llm-deployment
```

### Test the API
```bash
# Health check
curl http://localhost:7860/health

# Test deployment (replace with your values)
curl -X POST http://localhost:7860/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "23f2001849@ds.study.iitm.ac.in",
    "task": "deploy",
    "round": 1,
    "nonce": "test-001",
    "brief": {
      "name": "Test App",
      "description": "Testing deployment"
    },
    "checks": ["has_readme", "has_license"],
    "evaluation_url": "https://httpbin.org/post",
    "secret": "student_secret_123"
  }'
```

### Access API Documentation

Open your browser and navigate to:
- **Swagger UI:** [http://localhost:7860/docs](http://localhost:7860/docs)
- **ReDoc:** [http://localhost:7860/redoc](http://localhost:7860/redoc)

---

## 🚀 Deployment

### Deploy to Hugging Face Spaces

1. **Create a new Space:**
   - Go to [https://huggingface.co/new-space](https://huggingface.co/new-space)
   - Name: `llm-code-deployment`
   - SDK: Docker
   - Hardware: CPU Basic (free tier)

2. **Clone the Space repository:**
```bash
   git clone https://huggingface.co/spaces/YOUR-USERNAME/llm-code-deployment
   cd llm-code-deployment
```

3. **Copy project files:**
```bash
   cp -r /path/to/your/project/* .
```

4. **Configure Secrets in Huggingface:**
   - Go to Space Settings → Repository secrets
   - Add all 7 required secrets:
     - `GITHUB_TOKEN`
     - `GITHUB_USERNAME`
     - `OPENAI_API_KEY`
     - `ALLOWED_SECRETS`
     - `API_HOST` (set to `0.0.0.0`)
     - `API_PORT` (set to `7860`)
     - `DEBUG` (set to `false`)

5. **Push to Hugging Face:**
```bash
   git add .
   git commit -m "Initial deployment"
   git push
```

6. **Wait for build:**
   - Space will show "Building" status
   - Wait 5-10 minutes for first build
   - Status will change to "Running" when ready

7. **Verify deployment:**
```bash
   curl https://YOUR-USERNAME-llm-code-deployment.hf.space/health
```

---

## 📁 Project Structure
```
llm-code-deployment/
├── app.py                      # Main FastAPI application
├── config.py                   # Configuration management
├── github_client.py            # GitHub API integration
├── llm_generator.py            # LLM code generation
├── evaluation_client.py        # Evaluation callback handler
├── utils.py                    # Helper functions
├── run.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── README.md                   # This file
├── LICENSE                     # MIT License
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── .dockerignore               # Docker ignore rules
└── setup_environment.py        # Automated setup script
```

---

## 💡 Usage Examples

### Example 1: Deploy a Portfolio Website
```bash
curl -X POST https://Krishna-11Analyst-llm-code-deployment.hf.space/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "23f2001849@ds.study.iitm.ac.in",
    "task": "deploy",
    "round": 1,
    "nonce": "portfolio-001",
    "brief": {
      "name": "John Doe Portfolio",
      "description": "Professional portfolio website showcasing web development projects, skills, and contact information"
    },
    "checks": ["has_readme", "has_license", "has_actions"],
    "evaluation_url": "https://evaluation-server.com/callback",
    "secret": "student_secret_123"
  }'
```

### Example 2: Deploy a Landing Page
```bash
curl -X POST https://Krishna-11Analyst-llm-code-deployment.hf.space/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "23f2001849@ds.study.iitm.ac.in",
    "task": "deploy",
    "round": 1,
    "nonce": "landing-001",
    "brief": {
      "name": "Product Launch",
      "description": "Modern landing page for SaaS product with hero section, features, pricing, and call-to-action"
    },
    "checks": ["has_readme", "has_license", "responsive_design"],
    "evaluation_url": "https://evaluation-server.com/callback",
    "secret": "student_secret_123"
  }'
```

### Example 3: Update Existing Application
```bash
curl -X POST https://Krishna-11Analyst-llm-code-deployment.hf.space/update \
  -H "Content-Type: application/json" \
  -d '{
    "email": "23f2001849@ds.study.iitm.ac.in",
    "task": "update",
    "round": 2,
    "nonce": "update-001",
    "brief": {
      "name": "Enhanced Portfolio",
      "description": "Add dark mode toggle, contact form with validation, and smooth scroll animations"
    },
    "checks": ["has_readme", "has_license", "dark_mode", "animations"],
    "evaluation_url": "https://evaluation-server.com/callback",
    "secret": "student_secret_123"
  }'
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. **422 Validation Error**

**Problem:** Request returns 422 Unprocessable Entity

**Solutions:**
- ✅ Ensure `brief` is an object `{"name": "...", "description": "..."}`, not a string
- ✅ Verify `round` is an integer (1, 2, 3...), not a string
- ✅ Check all required fields are present: `email`, `task`, `round`, `nonce`, `brief`, `checks`, `evaluation_url`, `secret`
- ✅ Use valid JSON format (no trailing commas, proper quotes)

#### 2. **401 Unauthorized / 403 Forbidden**

**Problem:** Authentication failed

**Solutions:**
- ✅ Verify `secret` matches one in `ALLOWED_SECRETS` environment variable
- ✅ Check for typos in secret value
- ✅ Ensure no extra spaces in secret

#### 3. **GitHub API Errors**

**Problem:** Repository creation fails

**Solutions:**
- ✅ Verify GitHub token has `repo` and `workflow` permissions
- ✅ Check token hasn't expired (generate new token if needed)
- ✅ Ensure `GITHUB_USERNAME` is correct
- ✅ Check GitHub API rate limits: [https://api.github.com/rate_limit](https://api.github.com/rate_limit)

#### 4. **OpenAI API Errors**

**Problem:** Code generation fails

**Solutions:**
- ✅ Verify OpenAI API key is valid
- ✅ Check account has available credits: [https://platform.openai.com/account/usage](https://platform.openai.com/account/usage)
- ✅ Ensure model access (GPT-4 or GPT-3.5-turbo)
- ✅ Check OpenAI service status: [https://status.openai.com](https://status.openai.com)

#### 5. **Deployment Takes Too Long**

**Problem:** Deployment doesn't complete

**Solutions:**
- ✅ Normal deployment time: 60-120 seconds
- ✅ Check Huggingface Spaces logs for errors
- ✅ Verify GitHub Actions workflow completed: Repository → Actions tab
- ✅ Wait for GitHub Pages to propagate (can take 1-2 minutes)

#### 6. **GitHub Pages Not Accessible**

**Problem:** Pages URL returns 404

**Solutions:**
- ✅ Wait 2-3 minutes after workflow completion for Pages to deploy
- ✅ Check repository Settings → Pages is enabled
- ✅ Verify source is set to "GitHub Actions"
- ✅ Check workflow logs for deployment errors
- ✅ Try accessing in incognito mode (cache issue)

#### 7. **400 Error: "Use /update for rounds 2+"**

**Problem:** Sent round 2+ to /deploy endpoint

**Solution:**
- ✅ Use `/deploy` for `round: 1` only
- ✅ Use `/update` for `round: 2, 3, 4...`

---

## 📊 Performance Metrics

| Metric | Average Time |
|--------|-------------|
| Request Validation | < 100ms |
| LLM Code Generation | 25-35 seconds |
| GitHub Repo Creation | 2-4 seconds |
| Files Commit | 3-5 seconds |
| GitHub Actions Setup | 2-4 seconds |
| Pages Deployment | 35-50 seconds |
| **Total End-to-End** | **70-100 seconds** |

---

## 🧪 Testing Checklist

Before submission, verify:

- [ ] Health endpoint returns 200 OK
- [ ] Deploy endpoint accepts Round 1 requests
- [ ] Update endpoint accepts Round 2+ requests
- [ ] GitHub repository is created successfully
- [ ] Repository contains: index.html, README.md, LICENSE
- [ ] GitHub Actions workflow exists and runs
- [ ] GitHub Pages site is live and accessible
- [ ] Evaluation callback is attempted
- [ ] All logs show successful completion

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
MIT License

Copyright (c) 2025 23f2001849

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👨‍💻 Author

**Student ID:** 23f2001849  
**Email:** 23f2001849@ds.study.iitm.ac.in  
**Course:** IITM Tools in Data Science - Project 1  
**Semester:** October 2025

### Links

- **Live API:** [https://Krishna-11Analyst-llm-code-deployment.hf.space](https://Krishna-11Analyst-llm-code-deployment.hf.space)
- **API Documentation:** [https://Krishna-11Analyst-llm-code-deployment.hf.space/docs](https://Krishna-11Analyst-llm-code-deployment.hf.space/docs)
- **GitHub Repository:** [https://github.com/23f2001849/llm-code-deployment](https://github.com/23f2001849/llm-code-deployment)
- **Example Deployment:** [https://23f2001849.github.io/llm-app-078f40-bc8135-609954](https://23f2001849.github.io/llm-app-078f40-bc8135-609954)

---

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **OpenAI** for GPT-4 API access
- **GitHub** for repository hosting and Pages
- **Hugging Face** for Spaces deployment platform
- **IITM** for the learning opportunity

---

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review API documentation at `/docs` endpoint
3. Check Huggingface Spaces logs
4. Contact: 23f2001849@ds.study.iitm.ac.in

---

**⭐ If you found this project helpful, please star the repository!**

**Built with ❤️ for IITM TDS Project-1**