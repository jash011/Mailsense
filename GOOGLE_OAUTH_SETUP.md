# 🔧 Google OAuth Setup Guide

## Error: "mailsense has not completed the Google verification process"

This error occurs because your Google Cloud Console project needs to be configured for testing. Here's how to fix it:

### Step 1: Access Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to "APIs & Services" > "OAuth consent screen"

### Step 2: Configure OAuth Consent Screen
1. **User Type**: Select "External" (unless you have a Google Workspace organization)
2. **App Information**:
   - App name: "MailSense Email Classifier"
   - User support email: Your email
   - Developer contact information: Your email
3. **Scopes**: Add these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/gmail.labels`
4. **Test Users**: Add your email address as a test user

### Step 3: Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Application type: "Desktop application"
4. Name: "MailSense Desktop Client"
5. Download the credentials file and rename it to `credentials.json`
6. Place `credentials.json` in the project root directory

### Step 4: Enable Gmail API
1. Go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on it and press "Enable"

### Step 5: Test the Setup
1. Set `TEST_MODE = False` in `mailsense/gmail_api.py`
2. Run the application
3. The first time you run it, a browser window will open for OAuth authentication

### Alternative: Use Test Mode (Current Setup)
The application is currently configured to run in TEST MODE, which means:
- ✅ No Google OAuth authentication required
- ✅ Mock data is used for testing
- ✅ All classification features work
- ✅ Perfect for development and testing

To switch to production mode:
1. Follow steps 1-4 above
2. Set `TEST_MODE = False` in `mailsense/gmail_api.py`
3. Restart the application

## Current Status: ✅ TEST MODE ACTIVE
The application is running in test mode and fully functional for development! 