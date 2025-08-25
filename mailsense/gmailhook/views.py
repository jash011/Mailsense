import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gmail_api import (
    get_gmail_service,
    get_latest_message,
    create_or_get_label,
    apply_label,
    get_message_content,
    get_message_metadata,
    get_messages_for_all_categories,
)
from googleapiclient.errors import HttpError
from classifiers import classify_email_content, extract_plain_text, has_links
from aimodel import predict_intent, classify_email_sentiment, classify_email_priority, extract_keywords, get_email_summary

@csrf_exempt
def gmail_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST supported'}, status=405)

    try:
        service = get_gmail_service()

        # Step 1: Get recent emails across Inbox and category tabs
        messages = get_messages_for_all_categories(service, max_per_category=20)
        if not messages:
            return JsonResponse({"status": "success", "result": {"processed": 0, "details": []}})

        processed_details = []
        processed_count = 0

        for message in messages:
            try:
                msg_id = message['id']
                payload = message.get('payload', {})

                # Rule-based classification
                rule_result = classify_email_content(payload)

                # Extract text content
                text = get_message_content(message)

                # AI classification
                label_ai = "AI:Unknown"
                if text.strip():
                    intent, confidence = predict_intent(text)
                    label_ai = f"AI:{intent.capitalize()}"
                else:
                    intent = None
                    confidence = 0.0

                # Build labels
                labels = []
                labels.append("Contains Link" if rule_result['link'] else "Text Only")
                if rule_result['suspicious']:
                    labels.append("Potential Phishing" if rule_result['money_related'] else "Suspicious Content")
                if rule_result['urgent_language']:
                    labels.append("Urgent Language")
                if rule_result['money_related']:
                    labels.append("Money Related")

                # Apply labels with retry
                def resolve_label_ids():
                    ids = [create_or_get_label(service, l) for l in labels]
                    ids.append(create_or_get_label(service, label_ai))
                    return ids

                label_ids = resolve_label_ids()
                try:
                    apply_label(service, msg_id, label_ids)
                except HttpError:
                    label_ids = resolve_label_ids()
                    apply_label(service, msg_id, label_ids)

                detail = {
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
                processed_details.append(detail)
                processed_count += 1
            except Exception as e:
                processed_details.append({"message_id": message.get('id'), "error": str(e)})

        return JsonResponse({"status": "success", "result": {"processed": processed_count, "details": processed_details}})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
