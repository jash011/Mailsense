import os
import json
from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

# Production mode - requires Google OAuth authentication
TEST_MODE = False

def check_credentials_file():
    """
    Check if credentials.json file exists in the correct location.
    
    Returns:
        bool: True if file exists, False otherwise
    """
    # Check in current directory
    if os.path.exists('credentials.json'):
        return True
    
    # Check in parent directory (project root)
    if os.path.exists('../credentials.json'):
        return True
    
    return False

def get_credentials_path():
    """
    Get the path to the credentials.json file.
    
    Returns:
        str: Path to credentials file
    """
    if os.path.exists('credentials.json'):
        return 'credentials.json'
    elif os.path.exists('../credentials.json'):
        return '../credentials.json'
    else:
        raise FileNotFoundError(
            "credentials.json not found. Please download it from Google Cloud Console "
            "and place it in the project root directory."
        )

def get_gmail_service():
    """
    Get authenticated Gmail service instance.
    
    Returns:
        Gmail service object
    """
    creds = None
    
    # Load existing credentials from token.pickle
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load client secrets
            credentials_path = get_credentials_path()
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def get_latest_message(service) -> Dict[str, Any]:
    """
    Get the latest message from the inbox.
    
    Args:
        service: Gmail service object
        
    Returns:
        Latest message object
    """
    try:
        # Get messages from inbox
        results = service.users().messages().list(
            userId='me', 
            labelIds=['INBOX'],
            maxResults=1
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            raise Exception("No messages found in inbox")
        
        # Get full message details
        message_id = messages[0]['id']
        message = service.users().messages().get(
            userId='me', 
            id=message_id,
            format='full'
        ).execute()
        
        return message
        
    except HttpError as error:
        raise Exception(f"Gmail API error: {error}")

def create_or_get_label(service, label_name: str) -> str:
    """
    Create a new label or get existing one by name.
    
    Args:
        service: Gmail service object
        label_name: Name of the label
        
    Returns:
        Label ID
    """
    try:
        # First, try to find existing label
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        for label in labels:
            if label['name'] == label_name:
                return label['id']
        
        # Create new label if not found
        label_object = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        
        created_label = service.users().labels().create(
            userId='me', 
            body=label_object
        ).execute()
        
        return created_label['id']
        
    except HttpError as error:
        raise Exception(f"Error creating/getting label: {error}")

def apply_label(service, message_id: str, label_ids: List[str]):
    """
    Apply labels to a message.
    
    Args:
        service: Gmail service object
        message_id: ID of the message
        label_ids: List of label IDs to apply
    """
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': label_ids}
        ).execute()
        
    except HttpError as error:
        raise Exception(f"Error applying labels: {error}")

def get_message_content(message: Dict[str, Any]) -> str:
    """
    Extract text content from a Gmail message.
    
    Args:
        message: Gmail message object
        
    Returns:
        Extracted text content
    """
    payload = message.get('payload', {})
    content = ""
    
    def extract_from_part(part):
        nonlocal content
        
        mime_type = part.get('mimeType', '')
        
        if 'text/plain' in mime_type:
            body = part.get('body', {})
            data = body.get('data')
            if data:
                import base64
                try:
                    text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    content += text + " "
                except Exception:
                    pass
        elif 'text/html' in mime_type:
            body = part.get('body', {})
            data = body.get('data')
            if data:
                import base64
                try:
                    html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    # Basic HTML to text conversion
                    import re
                    text = re.sub(r'<[^>]+>', '', html)
                    text = re.sub(r'\s+', ' ', text).strip()
                    content += text + " "
                except Exception:
                    pass
        elif 'multipart' in mime_type:
            parts = part.get('parts', [])
            for sub_part in parts:
                extract_from_part(sub_part)
    
    extract_from_part(payload)
    return content.strip()

def get_message_metadata(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a Gmail message.
    
    Args:
        message: Gmail message object
        
    Returns:
        Dictionary with message metadata
    """
    headers = message.get('payload', {}).get('headers', [])
    metadata = {}
    
    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')
        
        if name == 'from':
            metadata['from'] = value
        elif name == 'to':
            metadata['to'] = value
        elif name == 'subject':
            metadata['subject'] = value
        elif name == 'date':
            metadata['date'] = value
    
    metadata['id'] = message.get('id')
    metadata['thread_id'] = message.get('threadId')
    metadata['label_ids'] = message.get('labelIds', [])
    
    return metadata
