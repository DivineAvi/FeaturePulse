import React, { useState, useEffect, type ReactElement } from 'react';
import Dashboard from './components/Dashboard';
import Competitors from './components/Competitors';
import Changes from './components/Changes';
import Reports from './components/Reports';
import Analytics from './components/Analytics';
import Settings from './components/Settings';
import AddCompetitorModal from './components/modals/AddCompetitorModal';
import CompetitorDetailModal from './components/modals/CompetitorDetailModal';
import type { Change, Competitor, DashboardData, Insights, TabName, TrackingStatusState, Report } from './types';
import { BarChart3, FileText, Settings as SettingsIcon, Target, Bell, Activity, AlertTriangle, RefreshCw } from 'lucide-react';
import apiService from './services/api';

const CompetitorTracker: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabName>('dashboard');
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [trackingStatus, setTrackingStatus] = useState<TrackingStatusState>({ status: 'idle' });
  const [changes, setChanges] = useState<Change[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [selectedCompetitor, setSelectedCompetitor] = useState<Competitor | null>(null);
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filterType, setFilterType] = useState<string>('all');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const addCompetitor = async (competitor: Competitor): Promise<void> => {
    try {
      const response = await apiService.createCompetitor({
        name: competitor.name,
        website: competitor.website,
        category: competitor.category,
        tracking_urls: competitor.tracking_urls
      });
      
      // Refresh competitors list
      fetchCompetitors();
    } catch (err) {
      console.error('Failed to add competitor:', err);
      setError('Failed to add competitor');
    }
  };

  const fetchCompetitors = async () => {
    try {
      const data = await apiService.getCompetitors();
      setCompetitors(data);
    } catch (err) {
      console.error('Failed to fetch competitors:', err);
      setError('Failed to fetch competitors');
    }
  };

  const fetchDashboardData = async () => {
    try {
      const data = await apiService.getDashboardData();
      setDashboardData(data);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to fetch dashboard data');
    }
  };

  const fetchChanges = async () => {
    try {
      const data = await apiService.getChanges();
      setChanges(data);
    } catch (err) {
      console.error('Failed to fetch changes:', err);
      setError('Failed to fetch changes');
    }
  };

  const fetchReports = async () => {
    try {
      const data = await apiService.getReports();
      setReports(data);
    } catch (err) {
      console.error('Failed to fetch reports:', err);
      setError('Failed to fetch reports');
    }
  };

  const fetchInsights = async () => {
    try {
      const data = await apiService.getInsights();
      setInsights(data);
    } catch (err) {
      console.error('Failed to fetch insights:', err);
      setError('Failed to fetch insights');
    }
  };

  const fetchTrackingStatus = async () => {
    try {
      const data = await apiService.getTrackingStatus();
      setTrackingStatus(data);
    } catch (err) {
      console.error('Failed to fetch tracking status:', err);
    }
  };

  const refreshAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        fetchCompetitors(),
        fetchDashboardData(),
        fetchChanges(),
        fetchReports(),
        fetchInsights(),
        fetchTrackingStatus()
      ]);
    } catch (err) {
      console.error('Failed to refresh data:', err);
      setError('Failed to load data from server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshAllData();
  }, []);

  interface TabItem {
    id: TabName;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
  }

  const renderContent = (): ReactElement => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <Dashboard
            dashboardData={dashboardData}
            trackingStatus={trackingStatus}
            setTrackingStatus={setTrackingStatus}
            changes={changes}
            setActiveTab={setActiveTab}
          />
        );
      case 'competitors':
        return (
          <Competitors
            competitors={competitors}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            filterType={filterType}
            setFilterType={setFilterType}
            setShowAddModal={setShowAddModal}
            setSelectedCompetitor={setSelectedCompetitor}
          />
        );
      case 'changes':
        return <Changes dashboardData={dashboardData} changes={changes} />;
      case 'reports':
        return <Reports reports={reports} />;
      case 'analytics':
        return <Analytics insights={insights} />;
      case 'settings':
        return <Settings />;
      default:
        return (
          <Dashboard
            dashboardData={dashboardData}
            trackingStatus={trackingStatus}
            setTrackingStatus={setTrackingStatus}
            changes={changes}
            setActiveTab={setActiveTab}
          />
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading competitor data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Connection Error</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={refreshAllData}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Target className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">CompetitorTracker</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${trackingStatus.status === 'running' ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                <span className="text-sm text-gray-600">
                  {trackingStatus.status === 'running' ? 'Tracking Active' : 'Tracking Idle'}
                </span>
              </div>
              <button 
                onClick={refreshAllData}
                className="p-2 text-gray-400 hover:text-gray-600"
                title="Refresh data"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
              <button className="p-2 text-gray-400 hover:text-gray-600">
                <Bell className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex">
          <nav className="w-64 mr-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <ul className="space-y-2">
                {([
                  { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
                  { id: 'competitors', label: 'Competitors', icon: Target },
                  { id: 'changes', label: 'Changes', icon: Activity },
                  { id: 'reports', label: 'Reports', icon: FileText },
                  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
                  { id: 'settings', label: 'Settings', icon: SettingsIcon }
                ] as TabItem[]).map((item) => (
                  <li key={item.id}>
                    <button
                      onClick={() => setActiveTab(item.id)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        activeTab === item.id
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      }`}
                    >
                      <item.icon className="w-4 h-4" />
                      <span>{item.label}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </nav>

          <main className="flex-1">{renderContent()}</main>
        </div>
      </div>

      <AddCompetitorModal show={showAddModal} setShow={setShowAddModal} addCompetitor={addCompetitor} />
      <CompetitorDetailModal competitor={selectedCompetitor} setCompetitor={setSelectedCompetitor} changes={changes} />
    </div>
  );
};

export default CompetitorTracker;