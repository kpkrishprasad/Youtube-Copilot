import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv('URLTOTEXT_API_KEY')

if not api_token:
    print("❌ URLTOTEXT_API_KEY not set in .env file")
    exit(1)

headers = {
    'Authorization': f'Token {api_token}',
    'Content-Type': 'application/json'
}

# Make a minimal request to check credits
# Using a simple URL to minimize credit usage
payload = {
    "url": "https://example.com",
    "output_format": "text",
    "extract_main_content": False,
    "render_javascript": False
}

try:
    print("Checking URLToText API credit balance...\n")
    
    # Show local tracking
    tracker_path = 'credits_tracker.json'
    if os.path.exists(tracker_path):
        with open(tracker_path, 'r') as f:
            tracker = json.load(f)
        total_used = tracker.get('total_used', 0)
        initial = tracker.get('initial_balance', 0.02)
        remaining = initial - total_used
        print(f"📊 Local Usage Tracking:")
        print(f"   Initial balance: {initial:.5f}")
        print(f"   Total used: {total_used:.5f}")
        print(f"   Estimated remaining: {remaining:.5f}\n")
    
    response = requests.post(
        'https://urltotext.com/api/v1/urltotext/',
        headers=headers,
        json=payload,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        credits_used = data.get('credits_used', 'N/A')
        print(f"✅ API is working!")
        print(f"Credits used for this check: {credits_used}")
        print(f"\n💰 Check your full balance at: https://urltotext.com/account/")
        
    elif response.status_code == 402:
        print("❌ No credits remaining!")
        print("Add more credits at: https://urltotext.com/account/")
    else:
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

