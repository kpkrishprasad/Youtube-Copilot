import yt_dlp
import json

url = "https://www.youtube.com/watch?v=JoCG72QMRJE"

ydl_opts = {
    'skip_download': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['en'],
    'subtitlesformat': 'json3',
    'quiet': False,
    'no_warnings': False
}

try:
    print(f"Attempting to extract captions from: {url}\n")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("Extracting video info...")
        info = ydl.extract_info(url, download=False)
        
        print(f"Video title: {info.get('title')}")
        print(f"Duration: {info.get('duration')} seconds\n")
        
        # Try to get manual subtitles first, then auto-generated
        subtitles = info.get('subtitles', {}).get('en') or info.get('automatic_captions', {}).get('en')
        
        if not subtitles:
            print("❌ No subtitles available for this video")
        else:
            print(f"✅ Found {len(subtitles)} subtitle formats")
            
            # Find json3 format
            json3_sub = None
            for sub in subtitles:
                if sub.get('ext') == 'json3':
                    json3_sub = sub
                    break
            
            if not json3_sub:
                print("❌ Could not find json3 subtitles")
            else:
                print(f"✅ Found json3 subtitle URL")
                print(f"Subtitle URL: {json3_sub['url'][:100]}...\n")
                
                # Download subtitle data
                import urllib.request
                print("Downloading subtitle data...")
                with urllib.request.urlopen(json3_sub['url']) as response:
                    sub_data = json.loads(response.read().decode('utf-8'))
                
                # Parse and display first 5 captions
                print("\n✅ Successfully extracted captions! First 5 lines:\n")
                count = 0
                for event in sub_data.get('events', []):
                    if 'segs' in event and count < 5:
                        start_time = event.get('tStartMs', 0) / 1000
                        timestamp = f"{int(start_time // 60)}:{int(start_time % 60):02d}"
                        text = ''.join([seg.get('utf8', '') for seg in event['segs']])
                        if text.strip():
                            print(f"[{timestamp}] {text.strip()}")
                            count += 1
                
                print(f"\n✅ SUCCESS: Caption extraction is working!")
                
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
    if '429' in str(e):
        print("\n🚫 Your IP is rate-limited by YouTube. Solutions:")
        print("   1. Switch to mobile hotspot")
        print("   2. Use a VPN")
        print("   3. Wait 24 hours")

