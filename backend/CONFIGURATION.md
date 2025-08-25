# Environment Configuration Guide

## Required Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

### Essential Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
```

### Optional Variables

```bash
# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# App Configuration
ENVIRONMENT=development
DEBUG=true

# Crawling Configuration
MAX_PAGES_PER_SITE=10
CRAWL_DELAY=2
TRACKING_INTERVAL_HOURS=24
```

## How to Get API Keys

### 1. OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key and paste it in your `.env` file

### 2. MongoDB Connection
- **Local MongoDB**: `mongodb://localhost:27017/competitor_tracker`
- **MongoDB Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/competitor_tracker`

### 3. Slack Webhook (Optional)
1. Go to https://api.slack.com/apps
2. Create a new app
3. Enable "Incoming Webhooks"
4. Create a webhook for your channel
5. Copy the webhook URL

## Example .env File

```bash
# Copy this to backend/.env and fill in your values

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/competitor_tracker

# Slack Integration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX

# App Configuration
ENVIRONMENT=development
DEBUG=true

# Crawling Configuration
MAX_PAGES_PER_SITE=10
CRAWL_DELAY=2
TRACKING_INTERVAL_HOURS=24
```

## Testing Configuration

After setting up your `.env` file:

1. Start MongoDB (if using local)
2. Run the backend: `python server.py`
3. Test the health endpoint: `http://localhost:8000/api/health`

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure
- Use different keys for development and production
- Consider using a secrets manager for production
