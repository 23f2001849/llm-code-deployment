import openai
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing OpenAI API Connectivity...")

api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key: {api_key[:20]}...{api_key[-4:] if api_key else 'None'}")

# Test with different approaches
try:
    # Test 1: Simple request with short timeout
    client = openai.OpenAI(api_key=api_key, timeout=10.0)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say just 'OK'"}],
        max_tokens=5
    )
    print("✅ OpenAI API: Direct connection successful!")
    print(f"   Response: {response.choices[0].message.content}")
    
except openai.AuthenticationError:
    print("❌ OpenAI API: Authentication failed - Invalid API key")
except openai.RateLimitError:
    print("❌ OpenAI API: Rate limit exceeded")
except openai.APITimeoutError:
    print("❌ OpenAI API: Request timed out - Network issue")
except openai.APIConnectionError:
    print("❌ OpenAI API: Connection error - Check internet/firewall")
except Exception as e:
    print(f"❌ OpenAI API: {type(e).__name__}: {e}")
