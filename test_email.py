import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import datetime

# Test data
video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
summary = """🎯 Key Points:
• This is a test summary
• Testing email functionality
• Everything looks great!"""

timestamps = """⏱️ Important Moments:
0:00 - Introduction
1:30 - Main content
3:45 - Conclusion"""

chat_history = [
    {"text": "What is this video about?", "type": "user"},
    {"text": "This is a test video to demonstrate the email functionality.", "type": "bot"}
]

recipient_email = "krishprasad.tech@gmail.com"

try:
    print("Preparing test email...")
    
    # Render email template
    html_content = render_to_string('summary/email_summary.html', {
        'video_url': video_url,
        'summary': summary,
        'timestamps': timestamps,
        'chat_history': chat_history,
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p')
    })
    
    print(f"\nSending test email to: {recipient_email}")
    print(f"From: {os.getenv('EMAIL_HOST_USER')}")
    
    # Send email
    send_mail(
        subject='YouTube Copilot - Test Email',
        message='',  # Plain text version
        from_email=os.getenv('EMAIL_HOST_USER', 'noreply@youtubecopilot.com'),
        recipient_list=[recipient_email],
        html_message=html_content,
        fail_silently=False
    )
    
    print("\n✅ Email sent successfully!")
    print(f"Check your inbox at {recipient_email}")
    
except Exception as e:
    print(f"\n❌ Error sending email: {type(e).__name__}: {str(e)}")
    print("\nMake sure you've set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env file")
    print("Get Gmail App Password at: https://myaccount.google.com/apppasswords")

