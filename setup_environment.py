import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_environment_file():

    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please create it from .env.example")
        return False
    print("✅ .env file found")
    return True

def install_dependencies():
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    directories = ["logs", "attachments"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    return True

def check_github_token():
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    if not token or token == "your_github_personal_access_token_here":
        print("❌ GITHUB_TOKEN not properly set in .env file")
        return False
    print("✅ GitHub token configured")
    return True

def check_openai_key():
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY")
    if not key or key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not properly set in .env file")
        return False
    print("✅ OpenAI API key configured")
    return True

def setup_environment():
    print("🔧 Setting up LLM Code Deployment Environment")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_environment_file),
        ("GitHub Token", check_github_token),
        ("OpenAI Key", check_openai_key),
        ("Directories", create_directories),
        ("Dependencies", install_dependencies),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"n🔍 {check_name}...")
        if not check_func():
            all_passed = False
    
    print("n" + "=" * 50)
    if all_passed:
        print("🎉 Environment setup completed successfully!")
        print("nNext steps:")
        print("1. Run: python app.py")
        print("2. Test with: python test_deployment.py")
        print("3. Check API docs at: http://localhost:8000/docs")
    else:
        print("❌ Environment setup failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    setup_environment()
