#!/usr/bin/env python3
"""
Quick script to create all Docker configuration files
Run this to set up Docker for 100% diagram compliance
"""

import os

def create_dockerfile():
    """Create Dockerfile"""
    content = '''FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs attachments

ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=7860

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["python", "run.py"]
'''
    
    with open('Dockerfile', 'w') as f:
        f.write(content)
    print("✅ Created: Dockerfile")

def create_docker_compose():
    """Create docker-compose.yml"""
    content = '''version: '3.8'

services:
  llm-deployment-api:
    build: .
    container_name: llm-code-deployment
    ports:
      - "7860:7860"
    env_file:
      - .env
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=7860
      - DEBUG=true
    volumes:
      - ./logs:/app/logs
      - ./attachments:/app/attachments
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - deployment-network

networks:
  deployment-network:
    driver: bridge
'''
    
    with open('docker-compose.yml', 'w') as f:
        f.write(content)
    print("✅ Created: docker-compose.yml")

def create_dockerignore():
    """Create .dockerignore"""
    content = '''# Environment variables
.env
.env.local
.env.*.local

# Git
.git
.gitignore

# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs and data
logs/
*.log
attachments/

# OS
.DS_Store
Thumbs.db

# Backups
backups/
*.backup

# Testing
.pytest_cache/
.coverage

# Documentation (optional - include if you want)
# *.md
'''
    
    with open('.dockerignore', 'w') as f:
        f.write(content)
    print("✅ Created: .dockerignore")

def update_config_for_docker():
    """Check if config.py needs updating for Docker"""
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        if 'API_PORT = int(os.getenv("API_PORT", 8000))' in content:
            print("⚠️  Note: config.py uses port 8000 by default")
            print("   Docker will override this to 7860")
            print("   This is fine - Docker config takes precedence")
        elif 'API_PORT = int(os.getenv("API_PORT", 7860))' in content:
            print("✅ config.py already set for port 7860")
        
    except FileNotFoundError:
        print("❌ config.py not found!")

def check_prerequisites():
    """Check if required files exist"""
    required_files = [
        'app.py',
        'config.py',
        'github_client.py',
        'llm_generator.py',
        'evaluation_client.py',
        'utils.py',
        'run.py',
        'requirements.txt',
        '.env'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        return False
    
    print("✅ All required files present")
    return True

def main():
    print("🐳 Creating Docker Configuration Files")
    print("=" * 50)
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Cannot proceed without required files")
        return
    
    print()
    
    # Create Docker files
    create_dockerfile()
    create_docker_compose()
    create_dockerignore()
    
    print()
    update_config_for_docker()
    
    print()
    print("=" * 50)
    print("🎉 Docker files created successfully!")
    print()
    print("📋 Next steps:")
    print("  1. Review the created files (Dockerfile, docker-compose.yml)")
    print("  2. Ensure .env file has valid credentials")
    print("  3. Run: docker-compose up --build")
    print("  4. Test: curl http://localhost:7860/health")
    print()
    print("💡 Tip: Use Ctrl+C to stop the container")
    print("💡 Tip: Use 'docker-compose down' to remove it")

if __name__ == "__main__":
    main()