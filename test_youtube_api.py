from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

youtube_api_key = os.getenv('YOUTUBE_API_KEY')

if not youtube_api_key or youtube_api_key == 'your-youtube-api-key-here':
    print("❌ YouTube API key not configured in .env file")
    exit(1)

try:
    print("Testing YouTube Data API v3...\n")
    
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    
    # Search for videos
    search_request = youtube.search().list(
        part='snippet',
        q='python programming tutorial',
        type='video',
        maxResults=3
    )
    
    print("Sending search request...")
    search_results = search_request.execute()
    
    if search_results.get('items'):
        print(f"\n✅ SUCCESS: YouTube Data API is working!\n")
        print(f"Found {len(search_results['items'])} videos:\n")
        
        for idx, item in enumerate(search_results['items'], 1):
            video_title = item['snippet']['title']
            video_id = item['id']['videoId']
            print(f"{idx}. {video_title}")
            print(f"   Video ID: {video_id}")
            print(f"   URL: https://www.youtube.com/watch?v={video_id}\n")
        
        print("✅ Your YouTube Data API is NOT banned!")
    else:
        print("❌ No results returned")
        
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
    if '403' in str(e):
        print("\n🚫 API key issue - check your YouTube API key")
    elif '429' in str(e):
        print("\n🚫 Rate limit hit on YouTube Data API")

