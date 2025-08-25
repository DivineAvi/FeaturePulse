import React from 'react';
import { Users, Activity, FileText, Play, Square, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import type { DashboardData, TrackingStatusState, Change, TabName } from '../types';
import apiService from '../services/api';

interface DashboardProps {
  dashboardData: DashboardData | null;
  trackingStatus: TrackingStatusState;
  setTrackingStatus: (status: TrackingStatusState) => void;
  changes: Change[];
  setActiveTab: (tab: TabName) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ 
  dashboardData, 
  trackingStatus, 
  setTrackingStatus, 
  changes, 
  setActiveTab 
}) => {
  const startTracking = async () => {
    try {
      setTrackingStatus({ status: 'running' });
      await apiService.startTracking();
      // Refresh tracking status after a delay
      setTimeout(async () => {
        try {
          const status = await apiService.getTrackingStatus();
          setTrackingStatus(status);
        } catch (err) {
          console.error('Failed to get tracking status:', err);
        }
      }, 2000);
    } catch (error) {
      console.error('Failed to start tracking:', error);
      setTrackingStatus({ status: 'idle' });
    }
  };

  const stopTracking = async () => {
    try {
      await apiService.stopTracking();
      setTrackingStatus({ status: 'idle' });
    } catch (error) {
      console.error('Failed to stop tracking:', error);
    }
  };

  const changeTypeColors = {
    feature: '#10B981',
    pricing: '#F59E0B',
    ui: '#3B82F6',
    other: '#6B7280'
  };

  const recentChanges = changes.slice(0, 5);

  // Get tracking status display info
  const getTrackingStatusInfo = () => {
    switch (trackingStatus.status) {
      case 'running':
        return {
          text: 'Active',
          color: 'text-green-600',
          bgColor: 'bg-green-100',
          icon: <Activity className="w-6 h-6 text-green-600" />
        };
      case 'completed':
        return {
          text: 'Completed',
          color: 'text-blue-600',
          bgColor: 'bg-blue-100',
          icon: <CheckCircle className="w-6 h-6 text-blue-600" />
        };
      case 'error':
        return {
          text: 'Error',
          color: 'text-red-600',
          bgColor: 'bg-red-100',
          icon: <AlertTriangle className="w-6 h-6 text-red-600" />
        };
      default:
        return {
          text: 'Idle',
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
          icon: <Clock className="w-6 h-6 text-gray-600" />
        };
    }
  };

  const trackingStatusInfo = getTrackingStatusInfo();

  // Show loading state if dashboardData is null
  if (!dashboardData) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Monitor your competitors and track changes</p>
          </div>
        </div>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading dashboard data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Monitor your competitors and track changes</p>
        </div>
        <div className="flex space-x-3">
          {trackingStatus.status === 'idle' && (
            <button
              onClick={startTracking}
              className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Play className="w-4 h-4" />
              <span>Start Tracking</span>
            </button>
          )}
          {trackingStatus.status === 'running' && (
            <button
              onClick={stopTracking}
              className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
            >
              <Square className="w-4 h-4" />
              <span>Stop Tracking</span>
            </button>
          )}
          {trackingStatus.status === 'completed' && (
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 bg-green-100 text-green-800 px-3 py-2 rounded-lg">
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Tracking Completed</span>
              </div>
              <button
                onClick={startTracking}
                className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Play className="w-4 h-4" />
                <span>Start New Tracking</span>
              </button>
            </div>
          )}
          {trackingStatus.status === 'error' && (
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 bg-red-100 text-red-800 px-3 py-2 rounded-lg">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm font-medium">Tracking Session Failed</span>
              </div>
              <button
                onClick={startTracking}
                className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Play className="w-4 h-4" />
                <span>Retry Tracking</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Tracking Status Banner */}
      {trackingStatus.status === 'completed' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <div>
              <h3 className="text-sm font-medium text-green-800">Tracking Session Completed</h3>
              <p className="text-sm text-green-700">
                The competitor tracking session has finished successfully. Check the Changes and Reports sections for the latest updates.
              </p>
            </div>
          </div>
        </div>
      )}

      {trackingStatus.status === 'error' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Tracking Session Failed</h3>
              <p className="text-sm text-red-700">
                The competitor tracking session encountered an error. Please try again or check the system status.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Competitors</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.overview?.total_competitors || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recent Changes</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.overview?.recent_changes || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <FileText className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Reports Generated</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData.overview?.recent_reports || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className={`p-2 ${trackingStatusInfo.bgColor} rounded-lg`}>
              {trackingStatusInfo.icon}
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Tracking Status</p>
              <p className={`text-2xl font-bold ${trackingStatusInfo.color}`}>
                {trackingStatusInfo.text}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Change Types Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Types</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={Object.entries(dashboardData.change_types || {}).map(([key, value]) => ({
                  name: key,
                  value,
                  color: changeTypeColors[key as keyof typeof changeTypeColors] || '#6B7280'
                }))}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {Object.entries(dashboardData.change_types || {}).map(([key]) => (
                  <Cell key={key} fill={changeTypeColors[key as keyof typeof changeTypeColors] || '#6B7280'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Competitor Activity Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Competitor Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboardData.competitor_activity || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="recent_changes" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Changes */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Changes</h3>
          <button
            onClick={() => setActiveTab('changes')}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View All
          </button>
        </div>
        {recentChanges.length > 0 ? (
          <div className="space-y-3">
            {recentChanges.map((change) => (
              <div key={change.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    change.severity === 'high' ? 'bg-red-500' :
                    change.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}></div>
                  <div>
                    <p className="font-medium text-gray-900">{change.competitor_name || 'Unknown'}</p>
                    <p className="text-sm text-gray-600">{change.change_type}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">
                    {new Date(change.detected_at).toLocaleDateString()}
                  </p>
                  {change.severity && (
                    <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                      change.severity === 'high' ? 'bg-red-100 text-red-800' :
                      change.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {change.severity}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No recent changes detected</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;


