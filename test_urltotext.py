import requests
import json

# Your API token from the top of the page
API_TOKEN = "b8501727d781ddccf936400f177f0219c8849a16"

# Test YouTube URL
youtube_url = "https://www.youtube.com/watch?v=JoCG72QMRJE"

print(f"Testing URLToText API with YouTube video...\n")
print(f"URL: {youtube_url}\n")

headers = {
    'Authorization': f'Token {API_TOKEN}',
    'Content-Type': 'application/json'
}

payload = {
    "url": youtube_url,
    "output_format": "text",
    "extract_main_content": True,
    "render_javascript": True
}

try:
    print("Sending request to URLToText API...")
    response = requests.post(
        'https://urltotext.com/api/v1/urltotext/',
        headers=headers,
        json=payload
    )
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!\n")
        print(f"Page Title: {data['data'].get('page_title', 'N/A')}")
        print(f"Credits Used: {data.get('credits_used', 'N/A')}")
        print(f"Remaining Credits: Check your dashboard\n")
        
        content = data['data'].get('content', '')
        
        if content:
            print("Content Preview (first 500 chars):")
            print("-" * 50)
            print(content[:500])
            print("-" * 50)
            print(f"\nTotal content length: {len(content)} characters")
            
            # Check if it looks like a transcript
            if any(word in content.lower() for word in ['transcript', 'captions', 'subscribe']):
                print("\n✅ This might work for extracting YouTube content!")
            else:
                print("\n⚠️ Content doesn't look like a transcript")
        else:
            print("❌ No content returned")
            
    elif response.status_code == 402:
        print("❌ Insufficient credits")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {str(e)}")

