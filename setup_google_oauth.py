#!/usr/bin/env python3
"""
Google OAuth Setup Script for MailSense
This script helps you set up Google OAuth authentication for the Gmail API.
"""

import os
import sys
import json
from pathlib import Path

def check_credentials_file():
    """Check if credentials.json exists and is valid."""
    possible_paths = [
        'credentials.json',
        '../credentials.json',
        'mailsense/credentials.json'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    if 'installed' in data or 'web' in data:
                        print(f"✅ Found valid credentials.json at: {path}")
                        return path
                    else:
                        print(f"❌ Invalid credentials.json format at: {path}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in credentials.json at: {path}")
    
    return None

def test_oauth_setup():
    """Test the OAuth setup."""
    print("🧪 Testing OAuth Setup...")
    print()
    
    # Check credentials file
    creds_path = check_credentials_file()
    if not creds_path:
        print("❌ No valid credentials.json found!")
        return False
    
    # Test Gmail API connection
    try:
        sys.path.append('mailsense')
        from gmail_api import get_gmail_service
        
        print("🔐 Attempting to authenticate with Google...")
        service = get_gmail_service()
        
        print("📧 Testing Gmail API connection...")
        # Try to get user profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Successfully connected to Gmail API!")
        print(f"   Email: {profile.get('emailAddress', 'Unknown')}")
        print(f"   Messages Total: {profile.get('messagesTotal', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth setup failed: {e}")
        print()
        return False

def main():
    """Main setup function."""
    print("🚀 MailSense Google OAuth Setup")
    print("=" * 40)
    print()
    
    # Check if credentials exist
    creds_path = check_credentials_file()
    
    if creds_path:
        print("✅ Credentials file found!")
        print()
        
        # Test the setup
        if test_oauth_setup():
            print()
            print("🎉 Setup completed successfully!")
            print("You can now run the MailSense application.")
        else:
            print()
            print("❌ Setup failed. Please follow the instructions above.")
    else:
        print("❌ No credentials file found!")
        print()

if __name__ == "__main__":
    main() 