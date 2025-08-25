import React from 'react';
import { TrendingUp, Users, Activity, FileText, Play, Square, AlertTriangle } from 'lucide-react';
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Monitor your competitors and track changes</p>
        </div>
        <div className="flex space-x-3">
          {trackingStatus.status === 'idle' ? (
            <button
              onClick={startTracking}
              className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Play className="w-4 h-4" />
              <span>Start Tracking</span>
            </button>
          ) : (
            <button
              onClick={stopTracking}
              className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
            >
              <Square className="w-4 h-4" />
              <span>Stop Tracking</span>
            </button>
          )}
        </div>
      </div>

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
                {dashboardData?.overview.total_competitors || 0}
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
                {dashboardData?.overview.recent_changes || 0}
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
                {dashboardData?.overview.recent_reports || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Tracking Status</p>
              <p className="text-2xl font-bold text-gray-900">
                {trackingStatus.status === 'running' ? 'Active' : 'Idle'}
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
                data={Object.entries(dashboardData?.change_types || {}).map(([key, value]) => ({
                  name: key,
                  value,
                  color: changeTypeColors[key as keyof typeof changeTypeColors]
                }))}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {Object.entries(dashboardData?.change_types || {}).map(([key]) => (
                  <Cell key={key} fill={changeTypeColors[key as keyof typeof changeTypeColors]} />
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
            <BarChart data={dashboardData?.competitor_activity || []}>
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
        <div className="space-y-4">
          {recentChanges.map((change) => (
            <div key={change.id} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
              <div className={`p-2 rounded-lg ${
                change.change_type === 'feature' ? 'bg-green-100' :
                change.change_type === 'pricing' ? 'bg-yellow-100' :
                change.change_type === 'ui' ? 'bg-blue-100' : 'bg-gray-100'
              }`}>
                {change.change_type === 'feature' && <TrendingUp className="w-4 h-4 text-green-600" />}
                {change.change_type === 'pricing' && <AlertTriangle className="w-4 h-4 text-yellow-600" />}
                {change.change_type === 'ui' && <Activity className="w-4 h-4 text-blue-600" />}
                {change.change_type === 'other' && <FileText className="w-4 h-4 text-gray-600" />}
              </div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">{change.competitor_name}</p>
                <p className="text-sm text-gray-600">{change.description}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">
                  {new Date(change.detected_at).toLocaleDateString()}
                </p>
                <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                  change.severity === 'high' ? 'bg-red-100 text-red-800' :
                  change.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {change.severity}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;


