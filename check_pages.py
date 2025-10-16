#!/usr/bin/env python3
"""
Check if GitHub Pages URLs are now live
"""
import requests
import time
from datetime import datetime

# Your two deployed apps from the logs
pages_urls = [
    "https://23f2001849.github.io/llm-app-6bf068-55502f-571834/",
    "https://23f2001849.github.io/llm-app-fda1bc-55502f-571981/"
]

print("🔍 Checking GitHub Pages Status...")
print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

for i, url in enumerate(pages_urls, 1):
    print(f"📄 App {i}: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Status: 200 OK - LIVE!")
            print(f"   📏 Size: {len(response.content)} bytes")
            
            # Check for total-sales element
            if 'total-sales' in response.text:
                print(f"   ✅ Found: #total-sales element")
            
            # Check for title
            if '<title>' in response.text:
                title_start = response.text.find('<title>') + 7
                title_end = response.text.find('</title>')
                title = response.text[title_start:title_end]
                print(f"   📝 Title: {title}")
                
        elif response.status_code == 404:
            print(f"   ⏳ Status: 404 - Still building (wait 1-2 more minutes)")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout - GitHub may be slow")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()

print("💡 If showing 404, wait 2-3 minutes and run this script again")
print("🔗 You can also check manually in your browser!")