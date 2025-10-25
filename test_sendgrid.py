import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('SENDGRID_API_KEY')

if not api_key:
    print("❌ SENDGRID_API_KEY not found in .env file")
    exit(1)

print(f"Using API key: {api_key[:10]}...")
print(f"\nSending test email to: krishprasad.tech@gmail.com\n")

message = Mail(
    from_email='krishprasad.tech@gmail.com',  # Your verified sender email
    to_emails='krishprasad.tech@gmail.com',
    subject='YouTube Copilot - SendGrid Test Email',
    html_content='<strong>🎉 SendGrid is working!</strong><br><br>Your YouTube Copilot email feature is now configured and ready to use.')

try:
    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    
    print(f"✅ Email sent successfully!")
    print(f"Status Code: {response.status_code}")
    print(f"\nCheck your inbox at krishprasad.tech@gmail.com")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nYou may need to verify your sender email:")
    print("1. Go to: https://app.sendgrid.com/settings/sender_auth/senders")
    print("2. Click 'Create New Sender'")
    print("3. Use: noreply@youtubecopilot.com or krishprasad.tech@gmail.com")
    print("4. Verify via email confirmation")

