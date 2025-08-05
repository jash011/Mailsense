import re
import base64
from typing import Dict, Any

def classify_email_content(payload: Dict[str, Any]) -> Dict[str, bool]:
    """
    Classify email content based on rule-based analysis.
    
    Args:
        payload: Gmail message payload
        
    Returns:
        Dictionary with classification results
    """
    result = {
        'text': False,
        'link': False,
        'suspicious': False,
        'urgent_language': False,
        'money_related': False
    }
    
    # Extract content from payload
    content_parts = extract_content_parts(payload)
    
    for content in content_parts:
        # Check for text content
        if content.strip():
            result['text'] = True
            
        # Check for links (URLs)
        if has_links(content):
            result['link'] = True
            
        # Check for suspicious patterns
        if is_suspicious_content(content):
            result['suspicious'] = True
            
        # Check for urgent language
        if has_urgent_language(content):
            result['urgent_language'] = True
            
        # Check for money-related content
        if has_money_related_content(content):
            result['money_related'] = True
    
    return result

def extract_content_parts(payload: Dict[str, Any]) -> list:
    """
    Extract text content from Gmail message payload.
    
    Args:
        payload: Gmail message payload
        
    Returns:
        List of text content strings
    """
    content_parts = []
    
    def extract_from_part(part):
        mime_type = part.get('mimeType', '')
        
        # Handle text content
        if 'text/plain' in mime_type or 'text/html' in mime_type:
            body = part.get('body', {})
            data = body.get('data')
            if data:
                try:
                    content = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    content_parts.append(content)
                except Exception:
                    pass
        
        # Handle multipart content
        elif 'multipart' in mime_type:
            parts = part.get('parts', [])
            for sub_part in parts:
                extract_from_part(sub_part)
    
    # Start extraction from main payload
    extract_from_part(payload)
    
    return content_parts

def has_links(content: str) -> bool:
    """
    Check if content contains URLs/links.
    
    Args:
        content: Text content to analyze
        
    Returns:
        True if links found, False otherwise
    """
    # URL patterns
    url_patterns = [
        r'https?://[^\s<>"]+|www\.[^\s<>"]+',  # HTTP/HTTPS and www URLs
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email addresses
        r'ftp://[^\s<>"]+',  # FTP URLs
    ]
    
    for pattern in url_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    
    return False


def is_suspicious_content(content: str) -> bool:
    """
    Check if content contains suspicious patterns that might indicate spam or phishing.
    
    Args:
        content: Text content to analyze
        
    Returns:
        True if suspicious patterns found, False otherwise
    """
    # Suspicious patterns
    suspicious_patterns = [
        r'urgent.*action.*required',
        r'account.*suspended',
        r'verify.*account',
        r'click.*here.*immediately',
        r'limited.*time.*offer',
        r'free.*money',
        r'lottery.*winner',
        r'bank.*transfer',
        r'password.*expired',
        r'security.*alert',
        r'unusual.*activity',
        r'login.*attempt',
        r'confirm.*details',
        r'update.*information',
        r'claim.*prize',
        r'congratulations.*winner',
        r'you.*won',
        r'claim.*reward',
        r'urgent.*response.*needed',
        r'account.*locked'
    ]
    
    content_lower = content.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return True
    
    return False


def has_urgent_language(content: str) -> bool:
    """
    Check if content contains urgent language patterns.
    
    Args:
        content: Text content to analyze
        
    Returns:
        True if urgent language found, False otherwise
    """
    urgent_patterns = [
        r'urgent',
        r'immediate.*action',
        r'act.*now',
        r'limited.*time',
        r'expires.*soon',
        r'last.*chance',
        r'final.*notice',
        r'deadline',
        r'asap',
        r'emergency',
        r'critical',
        r'important.*notice'
    ]
    
    content_lower = content.lower()
    for pattern in urgent_patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return True
    
    return False


def has_money_related_content(content: str) -> bool:
    """
    Check if content contains money-related patterns.
    
    Args:
        content: Text content to analyze
        
    Returns:
        True if money-related content found, False otherwise
    """
    money_patterns = [
        r'\$\d+',
        r'dollar',
        r'payment',
        r'invoice',
        r'bill',
        'bank.*account',
        r'credit.*card',
        r'paypal',
        r'bank.*transfer',
        r'wire.*transfer',
        r'check',
        r'cash',
        r'prize.*money',
        r'refund',
        r'payment.*due',
        r'overdue.*payment'
    ]
    
    content_lower = content.lower()
    for pattern in money_patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return True
    
    return False


def extract_plain_text(payload: Dict[str, Any]) -> str:
    """
    Extract plain text content from email payload.
    
    Args:
        payload: Gmail message payload
        
    Returns:
        Plain text content
    """
    content_parts = extract_content_parts(payload)
    text_content = []
    
    for content in content_parts:
        # Basic HTML tag removal
        clean_content = re.sub(r'<[^>]+>', '', content)
        # Remove extra whitespace
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        if clean_content:
            text_content.append(clean_content)
    
    return ' '.join(text_content)
