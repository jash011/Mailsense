import base64
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gmail_api import get_gmail_service, get_latest_message, create_or_get_label, apply_label, get_message_content, get_message_metadata
from classifiers import classify_email_content, extract_plain_text, has_links
from aimodel import predict_intent, classify_email_sentiment, classify_email_priority, extract_keywords, get_email_summary

@csrf_exempt
def gmail_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST supported'}, status=405)

    try:
        service = get_gmail_service()

        # Step 1: Get latest email from inbox
        message = get_latest_message(service)
        msg_id = message['id']
        payload = message['payload']

        # Step 2: Rule-based classification (text/link/image)
        rule_result = classify_email_content(payload)

        # Step 3: Extract plain text or HTML to run through AI
        text = get_message_content(message)

        # Step 4: AI-based classification (intent prediction)
        label_ai = "AI:Unknown"
        if text.strip():
            intent, confidence = predict_intent(text)
            label_ai = f"AI:{intent.capitalize()}"
        else:
            intent = None
            confidence = 0.0

        # Step 5: Create comprehensive labels based on analysis
        labels = []
        
        # Rule-based labels
        if rule_result['link']:
            labels.append("Contains Link")
        else:
            labels.append("Text Only")
            
        # Security and spam detection
        if rule_result['suspicious']:
            if rule_result['money_related']:
                labels.append("⚠️ Potential Phishing")
            else:
                labels.append("⚠️ Suspicious Content")
                
        # Urgent language detection
        if rule_result['urgent_language']:
            labels.append("🚨 Urgent Language")
            
        # Money-related content
        if rule_result['money_related']:
            labels.append("💰 Money Related")

        # Step 6: Apply all labels
        label_ids = []
        
        # Apply rule-based labels
        for label in labels:
            label_id = create_or_get_label(service, label)
            label_ids.append(label_id)
        
        # Apply AI label
        ai_label_id = create_or_get_label(service, label_ai)
        label_ids.append(ai_label_id)
        
        # Apply all labels to the message
        apply_label(service, msg_id, label_ids)

        # Step 7: Optional logging
        result = {
            "message_id": msg_id,
            "applied_labels": labels + [label_ai],
            "ai_label": label_ai,
            "intent": intent,
            "confidence": round(confidence, 2),
            "rule_classification": rule_result,
            "security_analysis": {
                "suspicious": rule_result['suspicious'],
                "urgent_language": rule_result['urgent_language'],
                "money_related": rule_result['money_related'],
                "potential_phishing": rule_result['suspicious'] and rule_result['money_related']
            }
        }

        print("Email classified:", json.dumps(result, indent=2))
        return JsonResponse({"status": "success", "result": result})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
