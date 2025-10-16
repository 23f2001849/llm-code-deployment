import requests
import json
import time
import base64

# Test configuration
API_BASE = "http://localhost:8000"
TEST_SECRET = "student_secret_123"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    print(f"Health status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{API_BASE}/")
    print(f"Root status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def create_test_deployment():
    """Test deployment with a simple task"""
    print("Testing deployment endpoint...")
    
    # Create a simple CSV file for testing
    csv_content = "name,salesnProduct A,100nProduct B,200nProduct C,150"
    csv_base64 = base64.b64encode(csv_content.encode()).decode()
    
    deployment_data = {
        "email": "test@example.com",
        "secret": TEST_SECRET,
        "task": "test-task-001",
        "round": 1,
        "nonce": "test-nonce-001",
        "brief": "Create a simple web page that displays a sales total from the attached CSV file. Show the total sales in a <h1> element with id 'total-sales'.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional", 
            "Page displays total sales in #total-sales element",
            "Page loads without errors"
        ],
        "evaluation_url": "https://httpbin.org/post",  # Using httpbin for testing
        "attachments": [
            {
                "name": "sales.csv",
                "url": f"data:text/csv;base64,{csv_base64}"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/deploy",
            json=deployment_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Deployment response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Deployment started successfully!")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"Deployment failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Deployment test error: {e}")
        return False

def test_invalid_secret():
    """Test deployment with invalid secret"""
    print("Testing invalid secret...")
    
    deployment_data = {
        "email": "test@example.com",
        "secret": "invalid_secret",
        "task": "test-task-002", 
        "round": 1,
        "nonce": "test-nonce-002",
        "brief": "Test brief",
        "checks": ["Test check"],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    response = requests.post(f"{API_BASE}/deploy", json=deployment_data)
    print(f"Invalid secret test: {response.status_code} (expected: 403)")
    return response.status_code == 403

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting LLM Code Deployment API Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Invalid Secret", test_invalid_secret),
        ("Deployment", create_test_deployment)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"n🧪 {test_name}")
            success = test_func()
            results.append((test_name, success))
            print(f"✅ {test_name}: PASSED" if success else f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("💡 Some tests failed. Check the configuration and logs.")

if __name__ == "__main__":
    run_all_tests()
