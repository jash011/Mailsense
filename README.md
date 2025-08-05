# MailSense - Email Processing and Classification System

MailSense is a Django-based application that automatically processes and classifies emails using both rule-based analysis and AI-powered intent detection. It integrates with Gmail API to fetch emails and apply intelligent labels based on content analysis.

## Features

- **Gmail Integration**: Seamless integration with Gmail API for email processing
- **Rule-based Classification**: Detects links, images, and text content in emails
- **AI-powered Intent Detection**: Uses zero-shot classification to identify email intent (newsletter, promotional, personal, work, etc.)
- **Sentiment Analysis**: Analyzes email tone and sentiment
- **Priority Classification**: Determines email priority levels
- **Automatic Labeling**: Applies intelligent labels to emails in Gmail
- **Keyword Extraction**: Extracts key terms from email content
- **Email Summarization**: Generates brief summaries of email content

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Gmail account with API access
- Google Cloud Console project

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Email-Proc
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Gmail API Setup

**Option A: Automated Setup (Recommended)**
```bash
python setup_google_oauth.py
```

**Option B: Manual Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API for your project
4. Configure OAuth Consent Screen:
   - Go to "APIs & Services" → "OAuth consent screen"
   - User Type: External
   - App name: MailSense Email Classifier
   - Add your email as test user
5. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the credentials JSON file
6. Rename the downloaded file to `credentials.json` and place it in the project root directory

### 5. Django Setup

```bash
cd mailsense
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

### 6. Run the Application

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## API Endpoints

### Gmail Webhook
- **URL**: `/gmail/webhook/`
- **Method**: POST
- **Description**: Processes the latest email from inbox and applies classification labels

## Usage

### First Run Authentication

On first run, the application will:
1. Open a browser window for Gmail authentication
2. Request permission to access your Gmail account
3. Save authentication tokens for future use

### Email Processing

The system automatically:
1. Fetches the latest email from your inbox
2. Analyzes content using rule-based classification
3. Performs AI-powered intent detection
4. Applies appropriate labels to the email
5. Returns classification results

## Classification Categories

### Rule-based Classification
- **Text Only**: Emails containing only text content
- **Contains Link**: Emails with URLs or links
- **⚠️ Suspicious Content**: Emails with suspicious patterns
- **⚠️ Potential Phishing**: Suspicious emails with money-related content
- **🚨 Urgent Language**: Emails with urgent or time-sensitive language
- **💰 Money Related**: Emails containing financial content

### AI Intent Classification
- **Newsletter**: Newsletters and subscriptions
- **Promotional**: Marketing and promotional emails
- **Personal**: Personal communications
- **Work**: Work-related emails
- **Notification**: System notifications
- **Spam**: Potential spam emails
- **Phishing**: Phishing attempts
- **Important**: Important communications
- **Urgent**: Urgent messages
- **Social**: Social media notifications
- **Shopping**: Shopping and e-commerce emails
- **Marketing**: Marketing communications

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Gmail API Scopes

The application uses the following Gmail API scopes:
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.modify`
- `https://www.googleapis.com/auth/gmail.labels`

## Project Structure

```
Email-Proc/
├── mailsense/
│   ├── gmailhook/          # Gmail integration app
│   │   ├── views.py        # Webhook endpoint
│   │   ├── models.py       # Database models
│   │   └── urls.py         # URL routing
│   ├── mailsense/          # Django project settings
│   │   ├── settings.py     # Django configuration
│   │   └── urls.py         # Main URL configuration
│   ├── classifiers.py      # Rule-based email classification
│   ├── gmail_api.py        # Gmail API integration
│   ├── aimodel.py          # AI-powered classification
│   └── manage.py           # Django management script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Troubleshooting

### Common Issues

1. **Gmail API Authentication Error**
   - Ensure `credentials.json` is in the project root
   - Check that Gmail API is enabled in Google Cloud Console
   - Verify OAuth consent screen is configured

2. **Model Loading Error**
   - Ensure you have sufficient disk space for model downloads
   - Check internet connection for initial model download
   - Verify transformers and torch are properly installed

3. **Permission Errors**
   - Ensure the application has necessary Gmail permissions
   - Check that the Gmail account has API access enabled

### Logs

Check Django logs for detailed error information:
```bash
python manage.py runserver --verbosity=2
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team. 