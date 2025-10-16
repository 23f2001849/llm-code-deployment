#!/usr/bin/env python3
"""
Comprehensive verification script for LLM Code Deployment System
Tests all components and provides detailed diagnostics
"""

import os
import sys
import time
import requests
import json
import base64
from dotenv import load_dotenv
from openai import OpenAI
from github import Github

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    print(f"  {text}")

# Load environment
load_dotenv()

def test_environment_variables():
    """Test 1: Environment Variables"""
    print_header("TEST 1: Environment Variables")
    
    required_vars = {
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'GITHUB_USERNAME': os.getenv('GITHUB_USERNAME'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ALLOWED_SECRETS': os.getenv('ALLOWED_SECRETS')
    }
    
    all_set = True
    for var, value in required_vars.items():
        if value and value not in ['your_github_token_here', 'your_openai_key_here']:
            print_success(f"{var} is set")
            if var == 'GITHUB_TOKEN' and not value.startswith('ghp_'):
                print_warning(f"{var} doesn't start with 'ghp_' - verify it's correct")
            elif var == 'OPENAI_API_KEY' and not value.startswith('sk-'):
                print_warning(f"{var} doesn't start with 'sk-' - verify it's correct")
        else:
            print_error(f"{var} is not set or has placeholder value")
            all_set = False
    
    return all_set

def test_github_connection():
    """Test 2: GitHub API Connection"""
    print_header("TEST 2: GitHub API Connection")
    
    token = os.getenv('GITHUB_TOKEN')
    username = os.getenv('GITHUB_USERNAME')
    
    if not token or not username:
        print_error("GitHub credentials not set")
        return False
    
    try:
        g = Github(token)
        user = g.get_user()
        
        print_success(f"Connected to GitHub as: {user.login}")
        print_info(f"Account created: {user.created_at}")
        print_info(f"Public repos: {user.public_repos}")
        
        # Check rate limit
        rate_limit = g.get_rate_limit()
        print_info(f"API Rate Limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
        
        if rate_limit.core.remaining < 100:
            print_warning("Low API rate limit remaining!")
        
        return True
        
    except Exception as e:
        print_error(f"GitHub connection failed: {e}")
        return False

def test_openai_connection():
    """Test 3: OpenAI API Connection"""
    print_header("TEST 3: OpenAI API Connection")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print_error("OpenAI API key not set")
        return False
    
    try:
        client = OpenAI(api_key=api_key, timeout=10.0)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Connection test successful'"}],
            max_tokens=10
        )
        
        reply = response.choices[0].message.content
        print_success("OpenAI API connection successful")
        print_info(f"Test response: {reply}")
        
        return True
        
    except Exception as e:
        print_error(f"OpenAI connection failed: {e}")
        return False

def test_api_server():
    """Test 4: Local API Server"""
    print_header("TEST 4: Local API Server")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            print_success("API server is running")
            health = response.json()
            print_info(f"Status: {health.get('status')}")
            
            components = health.get('components', {})
            for component, status in components.items():
                if status == 'ok':
                    print_success(f"{component}: {status}")
                else:
                    print_warning(f"{component}: {status}")
            
            return True
        else:
            print_error(f"Health check failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API server")
        print_info("Make sure the server is running with: python run.py")
        return False
    except Exception as e:
        print_error(f"API server test failed: {e}")
        return False

def test_deployment_endpoint():
    """Test 5: Deployment Endpoint"""
    print_header("TEST 5: Deployment Endpoint (Dry Run)")
    
    base_url = "http://localhost:8000"
    secret = os.getenv('ALLOWED_SECRETS', '').split(',')[0].strip()
    
    if not secret:
        print_error("No valid secret found in ALLOWED_SECRETS")
        return False
    
    # Create test data
    csv_content = "product,sales\nProduct A,100\nProduct B,200\nProduct C,150"
    csv_base64 = base64.b64encode(csv_content.encode()).decode()
    
    test_data = {
        "email": "test@example.com",
        "secret": secret,
        "task": f"verify-test-{int(time.time())}",
        "round": 1,
        "nonce": f"test-nonce-{int(time.time())}",
        "brief": "Create a simple web page that displays the total sales from the CSV. Show total in <h1 id='total-sales'>.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays total sales in #total-sales",
            "Page loads without errors"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": [
            {
                "name": "sales.csv",
                "url": f"data:text/csv;base64,{csv_base64}"
            }
        ]
    }
    
    try:
        print_info("Sending deployment request...")
        response = requests.post(
            f"{base_url}/deploy",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print_success("Deployment request accepted")
            result = response.json()
            print_info(f"Status: {result.get('status')}")
            print_info(f"Task ID: {result.get('task_id')}")
            print_info(f"Message: {result.get('message')}")
            print_warning("Check logs/deployment_*.log for detailed progress")
            return True
        else:
            print_error(f"Deployment failed: HTTP {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Deployment test failed: {e}")
        return False

def test_invalid_secret():
    """Test 6: Security - Invalid Secret"""
    print_header("TEST 6: Security Validation")
    
    base_url = "http://localhost:8000"
    
    test_data = {
        "email": "test@example.com",
        "secret": "invalid_secret_12345",
        "task": "security-test",
        "round": 1,
        "nonce": "test-nonce",
        "brief": "Test",
        "checks": ["Test"],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    try:
        response = requests.post(f"{base_url}/deploy", json=test_data)
        
        if response.status_code == 403:
            print_success("Security check passed - invalid secret rejected")
            return True
        else:
            print_error(f"Security check failed - got HTTP {response.status_code} instead of 403")
            return False
            
    except Exception as e:
        print_error(f"Security test failed: {e}")
        return False

def check_file_structure():
    """Test 7: Project File Structure"""
    print_header("TEST 7: Project File Structure")
    
    required_files = [
        'app.py',
        'config.py',
        'github_client.py',
        'llm_generator.py',
        'evaluation_client.py',
        'utils.py',
        '.env',
        'requirements.txt',
        'README.md'
    ]
    
    required_dirs = ['logs', 'attachments']
    
    all_present = True
    
    for file in required_files:
        if os.path.exists(file):
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            all_present = False
    
    for dir in required_dirs:
        if os.path.exists(dir):
            print_success(f"Found directory: {dir}/")
        else:
            print_warning(f"Missing directory: {dir}/ (will be created)")
            try:
                os.makedirs(dir, exist_ok=True)
                print_info(f"Created: {dir}/")
            except Exception as e:
                print_error(f"Failed to create {dir}/: {e}")
    
    return all_present

def run_full_verification():
    """Run all verification tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  LLM CODE DEPLOYMENT SYSTEM - VERIFICATION SUITE")
    print(f"{'='*60}{Colors.RESET}\n")
    
    tests = [
        ("File Structure", check_file_structure),
        ("Environment Variables", test_environment_variables),
        ("GitHub Connection", test_github_connection),
        ("OpenAI Connection", test_openai_connection),
        ("API Server", test_api_server),
        ("Deployment Endpoint", test_deployment_endpoint),
        ("Security Validation", test_invalid_secret)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! ({passed}/{total}){Colors.RESET}")
        print(f"\n{Colors.GREEN}Your system is ready for deployment!{Colors.RESET}")
        print(f"\nNext steps:")
        print(f"  1. Keep the server running: python run.py")
        print(f"  2. Submit your API endpoint to the Google Form")
        print(f"  3. Monitor logs/ directory for deployment status")
    else:
        print(f"{Colors.YELLOW}⚠ SOME TESTS FAILED ({passed}/{total} passed){Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please fix the issues above before deploying{Colors.RESET}")
        print(f"\nCommon fixes:")
        print(f"  - Update .env with valid credentials")
        print(f"  - Run: python run.py (in a separate terminal)")
        print(f"  - Install dependencies: pip install -r requirements.txt")
    
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    return passed == total

if __name__ == "__main__":
    success = run_full_verification()
    sys.exit(0 if success else 1)