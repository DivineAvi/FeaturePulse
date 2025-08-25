# FeaturePulse 🚀

A comprehensive competitor intelligence platform that automatically monitors competitors' websites, app stores, and social media to detect changes and provide actionable insights.

## 🌟 Features

### 🔍 **Multi-Source Monitoring**
- **Website Monitoring**: Tracks changes to competitor websites with intelligent crawling
- **App Store Tracking**: Monitors iOS App Store and Google Play Store updates
- **Social Media Intelligence**: Tracks LinkedIn and Twitter announcements
- **Smart Change Detection**: Uses content hashing and AI analysis to identify meaningful changes

### 📊 **Intelligent Analysis**
- **AI-Powered Insights**: Uses OpenAI to analyze and categorize changes
- **Change Classification**: Automatically categorizes changes as features, pricing, UI, or other
- **Competitive Intelligence**: Provides strategic insights and recommendations
- **Detailed Reporting**: Generates comprehensive weekly reports with competitor-specific details

### 📈 **Reporting & Notifications**
- **Weekly Reports**: Automated weekly competitor intelligence reports
- **Slack Integration**: Delivers reports directly to Slack channels
- **Detailed Analytics**: Tracks competitor changes over time
- **Actionable Insights**: Provides strategic recommendations for product teams

### 🎯 **User-Friendly Dashboard**
- **Modern React Frontend**: Built with React 19, TypeScript, and Tailwind CSS
- **Real-time Updates**: Live dashboard showing competitor activity
- **Competitor Management**: Add, edit, and manage competitor profiles
- **Change History**: View detailed change history and analysis

## 🏗️ Architecture

```
FeaturePulse/
├── backend/                 # FastAPI backend
│   ├── agent/              # AI agent for analysis
│   ├── database/           # MongoDB schemas and managers
│   ├── tools/              # Crawling and monitoring tools
│   ├── routes/             # API endpoints
│   └── server.py           # Main server file
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   └── package.json
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **MongoDB** (local or cloud)
- **OpenAI API Key**
- **Slack Webhook URL** (optional)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd FeaturePulse
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Create .env file
cp .env.example .env
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Environment Configuration

Create a `.env` file in the `backend` directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
MONGO_URI=mongodb://localhost:27017/featurepulse

# Slack Configuration (optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Tracking Configuration
MAX_PAGES_PER_SITE=10
MAX_SOCIAL_POSTS=10

# Schedule Configuration
WEEKLY_RUN_DAY=monday
WEEKLY_RUN_TIME=09:00
```

### 5. Start the Application

```bash
# Terminal 1: Start backend
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Visit `http://localhost:5173` to access the dashboard.

## 📋 Usage Guide

### Adding Competitors

1. Navigate to the **Competitors** section in the dashboard
2. Click **Add Competitor**
3. Fill in:
   - **Name**: Competitor company name
   - **Website**: Main website URL
   - **Category**: Business category
   - **Tracking URLs**: Additional URLs to monitor (app stores, social media, etc.)

### Monitoring Setup

The system automatically:
- **Crawls websites** for content changes
- **Monitors app stores** for updates
- **Tracks social media** for announcements
- **Analyzes changes** using AI
- **Generates reports** weekly

### Viewing Reports

- **Dashboard**: Overview of recent changes
- **Reports**: Detailed weekly competitor intelligence reports
- **Analytics**: Historical change tracking and trends
- **Settings**: Configure monitoring preferences

## 🔧 Configuration

### Backend Configuration

Key configuration options in `backend/config.py`:

```python
# Tracking limits
MAX_PAGES_PER_SITE = 10      # Max pages to crawl per website
MAX_SOCIAL_POSTS = 10        # Max social posts to track

# Schedule settings
WEEKLY_RUN_DAY = "monday"    # Day for weekly reports
WEEKLY_RUN_TIME = "09:00"    # Time for weekly reports

# Error handling
MAX_RETRIES = 3              # Retry attempts for failed operations
RETRY_DELAY_SECONDS = 60     # Delay between retries
```

### Frontend Configuration

The frontend uses Vite for development and building:

```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🛠️ Development

### Backend Development

```bash
cd backend

# Run tests
python -m pytest

# Format code
black .

# Lint code
flake8 .
```

### Frontend Development

```bash
cd frontend

# Run linter
npm run lint

# Type checking
npx tsc --noEmit
```

## 📊 API Endpoints

### Competitors
- `GET /api/competitors` - List all competitors
- `POST /api/competitors` - Add new competitor
- `PUT /api/competitors/{id}` - Update competitor
- `DELETE /api/competitors/{id}` - Delete competitor

### Changes
- `GET /api/changes` - List detected changes
- `GET /api/changes/{competitor_id}` - Get changes for specific competitor

### Reports
- `GET /api/reports` - List generated reports
- `POST /api/reports/generate` - Manually generate report

## 🔒 Security Considerations

- **API Keys**: Store sensitive keys in environment variables
- **CORS**: Configured to allow all origins (customize for production)
- **Rate Limiting**: Implement rate limiting for production use
- **Authentication**: Add user authentication for production deployment

## 🚀 Deployment

### Backend Deployment

```bash
# Build Docker image
docker build -t featurepulse-backend ./backend

# Run with environment variables
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e MONGO_URI=your_mongo_uri \
  featurepulse-backend
```

### Frontend Deployment

```bash
cd frontend

# Build for production
npm run build

# Deploy to your preferred hosting service
# (Vercel, Netlify, AWS S3, etc.)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `/docs` folder
- Review the configuration examples

## 🔄 Changelog

### v1.0.0
- Initial release
- Multi-source competitor monitoring
- AI-powered change analysis
- Weekly reporting system
- Modern React dashboard
- Slack integration

---

**FeaturePulse** - Stay ahead of the competition with intelligent competitor monitoring and analysis. 🎯 
