# Competitor Feature Tracker - Frontend

A modern React frontend for monitoring competitor websites, tracking changes, and generating intelligence reports.

## Features

- **Dashboard**: Overview of tracking status, metrics, and recent changes
- **Competitors**: Manage and monitor competitor profiles
- **Changes**: View and filter detected changes with detailed analysis
- **Reports**: Generate and view weekly competitor intelligence reports
- **Analytics**: Deep insights into competitor activity and trends
- **Settings**: Configure tracking preferences and notifications

## Tech Stack

- **React 19** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Recharts** for data visualization
- **Axios** for API communication
- **React Router** for navigation

## Getting Started

### Prerequisites

- Node.js 18+ 
- Backend server running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:5173](http://localhost:5173) in your browser

### Building for Production

```bash
npm run build
```

## API Integration

The frontend connects to the backend API at `http://localhost:8000/api`. Make sure your backend is running and MongoDB is connected.

### Key API Endpoints

- `GET /api/competitors` - List all competitors
- `POST /api/competitors` - Add new competitor
- `GET /api/analytics/dashboard` - Get dashboard data
- `POST /api/tracking/start` - Start competitor tracking
- `GET /api/changes` - Get detected changes
- `POST /api/reports/generate` - Generate weekly report

## Project Structure

```
src/
├── components/          # React components
│   ├── Dashboard.tsx    # Main dashboard
│   ├── Competitors.tsx  # Competitor management
│   ├── Changes.tsx      # Change tracking
│   ├── Reports.tsx      # Report generation
│   ├── Analytics.tsx    # Data analytics
│   ├── Settings.tsx     # Configuration
│   └── modals/          # Modal components
├── services/
│   └── api.ts          # API integration
├── types.ts            # TypeScript types
└── App.tsx             # Main application
```

## Usage

1. **Add Competitors**: Use the "Add Competitor" button to add new competitors with their websites and tracking URLs
2. **Start Tracking**: Click "Start Tracking" on the dashboard to begin monitoring
3. **View Changes**: Navigate to the Changes tab to see detected updates
4. **Generate Reports**: Create weekly intelligence reports in the Reports section
5. **Analyze Trends**: Use the Analytics tab for deeper insights

## Configuration

Update the API base URL in `src/services/api.ts` if your backend runs on a different port:

```typescript
const API_BASE_URL = 'http://localhost:8000/api';
```

## Development

- **Hot Reload**: Changes are automatically reflected in the browser
- **TypeScript**: Full type safety and IntelliSense support
- **ESLint**: Code quality and consistency
- **Tailwind**: Utility-first CSS framework for rapid UI development
