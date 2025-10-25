from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from .extract_caption import *
import google.generativeai as genai
from googleapiclient.discovery import build
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def index(request):
    return render(request, 'summary/index.html')




@csrf_exempt
def get_summary(request):
    if request.method == 'POST':
        try:
            youtube_link = request.POST.get('youtube_link')
            
            if not youtube_link:
                return JsonResponse({'error': 'No YouTube link provided'}, status=400)
            
            # Extract captions
            captions = extract_caption(youtube_link)
            
            if not captions:
                return JsonResponse({'error': 'Could not extract captions from video'}, status=400)
            
            # Generate summary and timestamps
            summary = create_summary_gpt(captions)
            timestamps = create_timestamps(captions)

            return JsonResponse({'summary': summary + '\n' + '\n' + timestamps})
            
        except Exception as e:
            return JsonResponse({'error': f'Error processing video: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def ask_question(request):
    """Handle Q&A about the video using Gemini"""
    if request.method == 'POST':
        try:
            youtube_link = request.POST.get('youtube_link')
            question = request.POST.get('question')
            
            if not youtube_link:
                return JsonResponse({'error': 'No YouTube link provided'}, status=400)
            
            if not question:
                return JsonResponse({'error': 'No question provided'}, status=400)
            
            # Extract captions
            captions = extract_caption(youtube_link)
            
            if not captions:
                return JsonResponse({'error': 'Could not extract captions from video'}, status=400)
            
            # Configure Gemini
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Create context from video captions
            caption_text = '\n'.join([f"{timestamp}: {text}" for timestamp, text in captions.items()])
            
            # Create prompt for Q&A
            prompt = f"""You are a helpful assistant answering questions about a YouTube video.

Video Transcript:
{caption_text}

User Question: {question}

Provide a clear, concise answer based on the video transcript. If the answer isn't in the transcript, say so."""
            
            # Get response from Gemini
            response = model.generate_content(prompt)
            answer = response.text
            
            return JsonResponse({'answer': answer})
            
        except Exception as e:
            return JsonResponse({'error': f'Error answering question: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def youtube_research(request):
    """Research a topic using multiple YouTube videos"""
    if request.method == 'POST':
        try:
            user_query = request.POST.get('query')
            
            if not user_query:
                return JsonResponse({'error': 'No query provided'}, status=400)
            
            # Step 1: Use Gemini to optimize the search query for YouTube
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            query_optimization_prompt = f"""Convert this user query into an optimal YouTube search query.
User wants to learn about: {user_query}

Provide ONLY the search query (no explanation, just the search terms).
Make it concise and YouTube-friendly."""
            
            search_response = model.generate_content(query_optimization_prompt)
            optimized_query = search_response.text.strip()
            
            # Step 2: Search YouTube for relevant videos
            youtube_api_key = os.getenv('YOUTUBE_API_KEY')
            
            if not youtube_api_key or youtube_api_key == 'your-youtube-api-key-here':
                return JsonResponse({'error': 'YouTube API key not configured. Add YOUTUBE_API_KEY to .env file.'}, status=500)
            
            youtube = build('youtube', 'v3', developerKey=youtube_api_key)
            
            search_request = youtube.search().list(
                part='snippet',
                q=optimized_query,
                type='video',
                maxResults=2,
                order='relevance',
                videoCategoryId='27'  # Education category
            )
            
            search_results = search_request.execute()
            
            if not search_results.get('items'):
                return JsonResponse({'error': 'No videos found for this query'}, status=404)
            
            # Step 3: Extract video information and captions
            video_data = []
            
            for item in search_results['items']:
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                try:
                    # Extract captions
                    captions = extract_caption(video_url)
                    
                    if captions:
                        # Get first 100 lines of captions
                        caption_text = '\n'.join([f"{k}: {v}" for k, v in list(captions.items())[:100]])
                        
                        video_data.append({
                            'title': video_title,
                            'url': video_url,
                            'captions': caption_text
                        })
                except:
                    # Skip videos without captions
                    continue
            
            if not video_data:
                return JsonResponse({'error': 'No videos with captions found'}, status=404)
            
            # Step 4: Use Gemini to create a comprehensive guide
            guide_prompt = f"""Create a comprehensive learning guide based on these YouTube videos about: {user_query}

Videos analyzed:
"""
            
            for idx, video in enumerate(video_data, 1):
                guide_prompt += f"\n\n=== Video {idx}: {video['title']} ===\n{video['url']}\n\nKey Content:\n{video['captions'][:1000]}...\n"
            
            guide_prompt += f"""\n\nCreate a structured learning guide that:
1. Provides an overview of {user_query}
2. Lists key concepts from the videos
3. Includes actionable takeaways
4. When referencing videos, use numbered links like [1], [2], [3], etc. corresponding to the video numbers above

IMPORTANT FORMATTING RULES:
- Do NOT use markdown formatting like ** or __ anywhere in your output
- Use plain text with emojis
- When referencing videos, use [1], [2], [3] etc. NOT "Video 1" or "Video 2"
- Example: "Learn about resume formatting from [1] and [5]"

Format with clear sections and bullet points using plain text only."""
            
            guide_response = model.generate_content(guide_prompt)
            guide = guide_response.text
            
            # Return the guide and video list
            return JsonResponse({
                'guide': guide,
                'videos': [{
                    'title': v['title'],
                    'url': v['url']
                } for v in video_data],
                'search_query': optimized_query
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error during research: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def email_summary(request):
    """Send video summary via email"""
    if request.method == 'POST':
        try:
            recipient_email = request.POST.get('email')
            video_url = request.POST.get('video_url')
            summary = request.POST.get('summary', '')
            timestamps = request.POST.get('timestamps', '')
            chat_history_json = request.POST.get('chat_history', '[]')
            
            if not recipient_email:
                return JsonResponse({'error': 'Email address is required'}, status=400)
            
            if not video_url:
                return JsonResponse({'error': 'Video URL is required'}, status=400)
            
            # Parse chat history
            import json
            try:
                chat_history = json.loads(chat_history_json)
            except:
                chat_history = []
            
            # Render email template
            html_content = render_to_string('summary/email_summary.html', {
                'video_url': video_url,
                'summary': summary,
                'timestamps': timestamps,
                'chat_history': chat_history,
                'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p')
            })
            
            # Send email via SendGrid
            sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
            from_email = os.getenv('EMAIL_HOST_USER', 'krishprasad.tech@gmail.com')
            
            if not sendgrid_api_key:
                return JsonResponse({'error': 'SendGrid API key not configured'}, status=500)
            
            message = Mail(
                from_email=from_email,
                to_emails=recipient_email,
                subject='YouTube Copilot - Video Summary',
                html_content=html_content
            )
            
            sg = SendGridAPIClient(sendgrid_api_key)
            sg.send(message)
            
            return JsonResponse({'success': True, 'message': 'Email sent successfully!'})
            
        except Exception as e:
            return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def email_research(request):
    """Send research guide via email"""
    if request.method == 'POST':
        try:
            recipient_email = request.POST.get('email')
            query = request.POST.get('query', '')
            search_query = request.POST.get('search_query', '')
            guide = request.POST.get('guide', '')
            videos_json = request.POST.get('videos', '[]')
            
            if not recipient_email:
                return JsonResponse({'error': 'Email address is required'}, status=400)
            
            if not query:
                return JsonResponse({'error': 'Research query is required'}, status=400)
            
            # Parse videos list
            import json
            try:
                videos = json.loads(videos_json)
            except:
                videos = []
            
            # Render email template
            html_content = render_to_string('summary/email_research.html', {
                'query': query,
                'search_query': search_query,
                'guide': guide,
                'videos': videos,
                'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p')
            })
            
            # Send email via SendGrid
            sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
            from_email = os.getenv('EMAIL_HOST_USER', 'krishprasad.tech@gmail.com')
            
            if not sendgrid_api_key:
                return JsonResponse({'error': 'SendGrid API key not configured'}, status=500)
            
            message = Mail(
                from_email=from_email,
                to_emails=recipient_email,
                subject=f'YouTube Copilot - Research Guide: {query[:50]}',
                html_content=html_content
            )
            
            sg = SendGridAPIClient(sendgrid_api_key)
            sg.send(message)
            
            return JsonResponse({'success': True, 'message': 'Email sent successfully!'})
            
        except Exception as e:
            return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)

