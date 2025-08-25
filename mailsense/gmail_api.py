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


TEST_MODE = False

def check_credentials_file():
    """
    Check if credentials.json file exists in the correct location.
    
    Returns:
        bool: True if file exists, False otherwise
    """

    if os.path.exists('credentials.json'):
        return True

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
    
    # Load existing creds from token.pickle
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_path = get_credentials_path()
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
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
        results = service.users().messages().list(
            userId='me', 
            labelIds=['INBOX'],
            maxResults=1
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            raise Exception("No messages found in inbox")
        
        message_id = messages[0]['id']
        message = service.users().messages().get(
            userId='me', 
            id=message_id,
            format='full'
        ).execute()
        
        return message
        
    except HttpError as error:
        raise Exception(f"Gmail API error: {error}")

def list_messages(service, label_ids: Optional[List[str]] = None, max_results: int = 50) -> List[Dict[str, Any]]:
    """
    List message metadata for given label IDs.
    
    Args:
        service: Gmail service object
        label_ids: Gmail label IDs to filter by
        max_results: Maximum messages to return
    
    Returns:
        List of message objects with id/threadId
    """
    try:
        params = {
            'userId': 'me',
            'maxResults': max_results
        }
        if label_ids:
            params['labelIds'] = label_ids
        results = service.users().messages().list(**params).execute()
        return results.get('messages', [])
    except HttpError as error:
        raise Exception(f"Gmail API error while listing messages: {error}")

def get_messages_for_all_categories(service, max_per_category: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch recent messages across Inbox and all Gmail category tabs.
    
    Categories include: INBOX, CATEGORY_PERSONAL, CATEGORY_PROMOTIONS, CATEGORY_SOCIAL, CATEGORY_UPDATES, CATEGORY_FORUMS.
    
    Args:
        service: Gmail service
        max_per_category: limit per category to avoid large scans
    
    Returns:
        List of full message objects (format='full'), de-duplicated
    """
    category_labels = [
        'INBOX',
        'CATEGORY_PERSONAL',
        'CATEGORY_PROMOTIONS',
        'CATEGORY_SOCIAL',
        'CATEGORY_UPDATES',
        'CATEGORY_FORUMS'
    ]

    seen_ids = set()
    messages_full: List[Dict[str, Any]] = []

    for label in category_labels:
        try:
            meta_list = list_messages(service, label_ids=[label], max_results=max_per_category)
            for meta in meta_list:
                msg_id = meta.get('id')
                if not msg_id or msg_id in seen_ids:
                    continue
                seen_ids.add(msg_id)
                message = service.users().messages().get(
                    userId='me', id=msg_id, format='full'
                ).execute()
                messages_full.append(message)
        except Exception:
            # Continue on category-specific errors
            continue

    return messages_full

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
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        for label in labels:
            if label.get('name') == label_name:
                return label.get('id')

        label_object = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }

        try:
            created_label = service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            return created_label.get('id')
        except HttpError:
            # If creation failed due to a transient state, re-list and return if found
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            for label in labels:
                if label.get('name') == label_name:
                    return label.get('id')
            raise

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
