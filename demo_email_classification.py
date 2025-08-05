#!/usr/bin/env python3
"""
Demo script showing enhanced email classification with spam, promotional, and phishing detection.
"""

import sys
import os

# Add the mailsense directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'mailsense'))

def demo_email_classification():
    """Demonstrate the enhanced email classification system."""
    
    print("🔍 MailSense Enhanced Email Classification Demo")
    print("=" * 60)
    
    try:
        from classifiers import (
            classify_email_content, 
            is_suspicious_content, 
            has_urgent_language, 
            has_money_related_content
        )
        from aimodel import predict_intent
        
        # Sample emails for demonstration
        sample_emails = [
            {
                "name": "Legitimate Newsletter",
                "content": "Hello! Here's our weekly newsletter with the latest tech updates and industry news.",
                "expected": "Normal newsletter content"
            },
            {
                "name": "Promotional Email",
                "content": "🎉 Special Offer! Get 50% off on all products. Limited time only! Visit our website now.",
                "expected": "Promotional with urgent language"
            },
            {
                "name": "Suspicious Phishing Attempt",
                "content": "URGENT: Your bank account has been suspended. Click here immediately to verify your details and avoid account closure. You need to update your payment information now.",
                "expected": "Phishing with urgent language and money content"
            },
            {
                "name": "Spam Lottery Email",
                "content": "CONGRATULATIONS! You've won $1,000,000 in our lottery! Claim your prize now by clicking here. Limited time offer!",
                "expected": "Spam with money and urgent language"
            },
            {
                "name": "Work Email",
                "content": "Hi team, please review the attached documents for tomorrow's meeting. Let me know if you have any questions.",
                "expected": "Normal work communication"
            }
        ]
        
        for i, email in enumerate(sample_emails, 1):
            print(f"\n📧 Email {i}: {email['name']}")
            print(f"Content: {email['content']}")
            print(f"Expected: {email['expected']}")
            
            # Create mock payload for classification
            import base64
            mock_payload = {
                'mimeType': 'text/plain',
                'body': {
                    'data': base64.urlsafe_b64encode(email['content'].encode('utf-8')).decode('utf-8')
                }
            }
            
            # Rule-based classification
            rule_result = classify_email_content(mock_payload)
            
            # AI classification
            intent, confidence = predict_intent(email['content'])
            
            # Determine labels
            labels = []
            
            if rule_result['link']:
                labels.append("Contains Link")
            else:
                labels.append("Text Only")
                
            if rule_result['suspicious']:
                if rule_result['money_related']:
                    labels.append("⚠️ Potential Phishing")
                else:
                    labels.append("⚠️ Suspicious Content")
                    
            if rule_result['urgent_language']:
                labels.append("🚨 Urgent Language")
                
            if rule_result['money_related']:
                labels.append("💰 Money Related")
            
            # AI label
            ai_label = f"AI:{intent.capitalize()}"
            labels.append(ai_label)
            
            print(f"📊 Analysis Results:")
            print(f"  • Rule Classification: {rule_result}")
            print(f"  • AI Intent: {intent} (confidence: {confidence:.2f})")
            print(f"  • Applied Labels: {', '.join(labels)}")
            
            # Security analysis
            security_analysis = {
                "suspicious": rule_result['suspicious'],
                "urgent_language": rule_result['urgent_language'],
                "money_related": rule_result['money_related'],
                "potential_phishing": rule_result['suspicious'] and rule_result['money_related']
            }
            
            print(f"  • Security Analysis: {security_analysis}")
            
            if security_analysis['potential_phishing']:
                print(f"  ⚠️  WARNING: This email shows signs of phishing!")
            elif security_analysis['suspicious']:
                print(f"  ⚠️  CAUTION: This email contains suspicious content!")
            
            print("-" * 60)
        
        print(f"\n🎯 Summary:")
        print(f"• The system now detects multiple types of problematic emails")
        print(f"• Rule-based analysis catches suspicious patterns")
        print(f"• AI classification provides intent detection")
        print(f"• Multiple labels can be applied to a single email")
        print(f"• Security analysis helps identify potential threats")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure all dependencies are installed and the system is properly configured.")

if __name__ == "__main__":
    demo_email_classification() 