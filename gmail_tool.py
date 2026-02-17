import os
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request  
from langchain.tools import tool

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Global variable to track sent emails and prevent duplicates
sent_emails_cache = set()

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email(to, subject, body):
    service = authenticate_gmail()

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={'raw': raw}
    ).execute()

    print("✅ Email Sent Successfully!")

@tool
def send_email_tool(email_details: str) -> str:
    """
    Send an email using Gmail API with user confirmation.
    
    Args:
        email_details: String containing email details in format 
                      "to=recipient@email.com; subject=Subject Line; body=Email content"
    
    Returns:
        Success or error message
    """
    try:
        # Parse the input string
        parts = email_details.split(';')
        
        to = ""
        subject = ""
        body = ""
        
        for part in parts:
            part = part.strip()
            if part.startswith('to='):
                to = part[3:].strip()
            elif part.startswith('subject='):
                subject = part[8:].strip()
            elif part.startswith('body='):
                body = part[5:].strip()
        
        # Validate inputs
        if not to or '@' not in to:
            return "Error: Invalid or missing recipient email address"
        
        if not subject:
            subject = "No Subject"
            
        if not body:
            body = "No content provided"
        
        # Create a unique identifier for this email
        email_id = f"{to}|{subject}|{body}"
        
        # Check if this exact email was already sent
        if email_id in sent_emails_cache:
            return f"⚠️ This email was already sent to {to}. Skipping duplicate."
        
        # Show email preview and ask for confirmation
        print("\n" + "="*50)
        print("📧 EMAIL PREVIEW")
        print("="*50)
        print(f"📧 To: {to}")
        print(f"📝 Subject: {subject}")
        print(f"📄 Body:\n{body}")
        print("="*50)
        
        # Ask for confirmation
        while True:
            confirm = input("\n🤔 Send this email? (yes/no/edit): ").lower().strip()
            
            if confirm in ['yes', 'y']:
                # Add to cache to prevent duplicates
                sent_emails_cache.add(email_id)
                
                # Send email
                send_email(to, subject, body)
                return f"✅ Email successfully sent to {to} with subject '{subject}'"
                
            elif confirm in ['no', 'n']:
                return f"❌ Email cancelled by user"
                
            elif confirm in ['edit', 'e']:
                print("\n✏️ Edit email:")
                new_to = input(f"To ({to}): ").strip() or to
                new_subject = input(f"Subject ({subject}): ").strip() or subject
                print(f"Current body: {body}")
                new_body = input("New body (or press Enter to keep current): ").strip() or body
                
                # Update values
                to, subject, body = new_to, new_subject, new_body
                email_id = f"{to}|{subject}|{body}"  # Update email ID
                
                print(f"\n📧 Updated email preview:")
                print(f"To: {to}")
                print(f"Subject: {subject}")
                print(f"Body: {body}")
                continue
                
            else:
                print("Please enter 'yes', 'no', or 'edit'")
        
    except KeyboardInterrupt:
        return "❌ Email cancelled by user (Ctrl+C)"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"