import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("🔧 Debugging LLM Code Deployment API...n")

# Test 1: Check environment variables
print("1. Checking environment variables...")
github_token = os.getenv('GITHUB_TOKEN')
github_username = os.getenv('GITHUB_USERNAME')
openai_key = os.getenv('OPENAI_API_KEY')
allowed_secrets = os.getenv('ALLOWED_SECRETS')

print(f"   GITHUB_TOKEN: {'✅ Set' if github_token and github_token != 'your_github_token_here' else '❌ Missing'}")
print(f"   GITHUB_USERNAME: {'✅ Set' if github_username and github_username != 'your_github_username' else '❌ Missing'}")
print(f"   OPENAI_API_KEY: {'✅ Set' if openai_key and openai_key != 'your_openai_key_here' else '❌ Missing'}")
print(f"   ALLOWED_SECRETS: {'✅ Set' if allowed_secrets else '❌ Missing'}")

# Test 2: Check API health
print("n2. Checking API health...")
try:
    health_response = requests.get('http://localhost:8000/health', timeout=5)
    print(f"   API Health: ✅ {health_response.status_code}")
    health_data = health_response.json()
    print(f"   Components: {health_data.get('components', {})}")
except Exception as e:
    print(f"   API Health: ❌ {e}")

# Test 3: Test OpenAI API
print("n3. Testing OpenAI API...")
if openai_key and openai_key != 'your_openai_key_here':
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello World'"}],
            max_tokens=10,
            timeout=10
        )
        print("   OpenAI API: ✅ Working")
        print(f"   Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"   OpenAI API: ❌ {e}")
else:
    print("   OpenAI API: ❌ No valid API key")

print("n🎯 Next steps: Check server logs for background processing errors!")
