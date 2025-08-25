from transformers import pipeline
from typing import Tuple, Optional
import logging

# Initialize the zero-shot classification pipeline
try:
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
except Exception as e:
    logging.error(f"Failed to load AI model: {e}")
    classifier = None

# Define email intent categories
EMAIL_INTENTS = [
    "newsletter",
    "promotional",
    "personal",
    "work",
    "notification",
    "spam",
    "phishing",
    "important",
    "urgent",
    "social",
    "shopping",
    "marketing"
]

def predict_intent(text: str) -> Tuple[str, float]:
    """
    Predict the intent of an email using zero-shot classification.
    
    Args:
        text: Email text content
        
    Returns:
        Tuple of (predicted_intent, confidence_score)
    """
    if not classifier:
        return "unknown", 0.0
    
    if not text or not text.strip():
        return "unknown", 0.0
    
    try:
        clean_text = text.strip()
        if len(clean_text) > 1000:
            clean_text = clean_text[:1000] + "..."
        
        result = classifier(
            clean_text,
            candidate_labels=EMAIL_INTENTS,
            hypothesis_template="This email is about {}."
        )
        
        predicted_intent = result['labels'][0]
        confidence = result['scores'][0]
        
        return predicted_intent, confidence
        
    except Exception as e:
        logging.error(f"Error in intent prediction: {e}")
        return "unknown", 0.0

def classify_email_sentiment(text: str) -> Tuple[str, float]:
    """
    Classify the sentiment of an email.
    
    Args:
        text: Email text content
        
    Returns:
        Tuple of (sentiment, confidence_score)
    """
    if not classifier:
        return "neutral", 0.0
    
    if not text or not text.strip():
        return "neutral", 0.0
    
    try:
        clean_text = text.strip()
        if len(clean_text) > 1000:
            clean_text = clean_text[:1000] + "..."
        
        result = classifier(
            clean_text,
            candidate_labels=["positive", "negative", "neutral"],
            hypothesis_template="This email has a {} tone."
        )
        
        predicted_sentiment = result['labels'][0]
        confidence = result['scores'][0]
        
        return predicted_sentiment, confidence
        
    except Exception as e:
        logging.error(f"Error in sentiment classification: {e}")
        return "neutral", 0.0

def classify_email_priority(text: str, subject: str = "") -> Tuple[str, float]:
    """
    Classify the priority level of an email.
    
    Args:
        text: Email text content
        subject: Email subject line
        
    Returns:
        Tuple of (priority_level, confidence_score)
    """
    if not classifier:
        return "normal", 0.0
    
    combined_text = f"Subject: {subject}\n\n{text}".strip()
    
    if not combined_text:
        return "normal", 0.0
    
    try:
        if len(combined_text) > 1000:
            combined_text = combined_text[:1000] + "..."
        
        result = classifier(
            combined_text,
            candidate_labels=["high", "normal", "low"],
            hypothesis_template="This email has {} priority."
        )
        
        predicted_priority = result['labels'][0]
        confidence = result['scores'][0]
        
        return predicted_priority, confidence
        
    except Exception as e:
        logging.error(f"Error in priority classification: {e}")
        return "normal", 0.0

def extract_keywords(text: str, max_keywords: int = 5) -> list:
    """
    Extract key terms from email text.
    
    Args:
        text: Email text content
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of extracted keywords
    """
    if not text or not text.strip():
        return []
    
    try:
        import re
        from collections import Counter
        
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()
        
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        keyword_counts = Counter(keywords)
        top_keywords = [word for word, count in keyword_counts.most_common(max_keywords)]
        
        return top_keywords
        
    except Exception as e:
        logging.error(f"Error in keyword extraction: {e}")
        return []

def get_email_summary(text: str, max_length: int = 200) -> str:
    """
    Generate a brief summary of the email content.
    
    Args:
        text: Email text content
        max_length: Maximum length of summary
        
    Returns:
        Email summary
    """
    if not text or not text.strip():
        return "No content available"
    
    try:
        import re

        sentences = re.split(r'[.!?]+', text.strip())

        sentences = [s.strip() for s in sentences if s.strip()]

        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip() or text[:max_length] + "..."
        
    except Exception as e:
        logging.error(f"Error in email summarization: {e}")
        return text[:max_length] + "..." if len(text) > max_length else text
