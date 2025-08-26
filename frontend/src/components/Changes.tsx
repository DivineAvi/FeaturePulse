import React, { useState } from 'react';
import { Filter, Calendar, AlertTriangle, TrendingUp, Activity, FileText } from 'lucide-react';
import type { DashboardData, Change } from '../types';

interface ChangesProps {
  dashboardData: DashboardData | null;
  changes: Change[];
}

const Changes: React.FC<ChangesProps> = ({ dashboardData, changes }) => {
  const [filterType, setFilterType] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('date');

  // Debug logging
  console.log('DEBUG: Changes component received changes:', changes);
  console.log('DEBUG: Changes component received dashboardData:', dashboardData);

  const filteredChanges = changes.filter(change => {
    const matchesType = filterType === 'all' || change.change_type === filterType;
    const matchesSeverity = filterSeverity === 'all' || change.severity === filterSeverity;
    return matchesType && matchesSeverity;
  }).sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime();
      case 'severity':
        const severityOrder = { high: 3, medium: 2, low: 1 };
        return severityOrder[b.severity as keyof typeof severityOrder] - severityOrder[a.severity as keyof typeof severityOrder];
      default:
        return 0;
    }
  });

  const getChangeTypeIcon = (type: string) => {
    switch (type) {
      case 'feature':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'pricing':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'ui':
        return <Activity className="w-4 h-4 text-blue-600" />;
      default:
        return <FileText className="w-4 h-4 text-gray-600" />;
    }
  };

  const getChangeTypeColor = (type: string) => {
    switch (type) {
      case 'feature':
        return 'bg-green-100 text-green-800';
      case 'pricing':
        return 'bg-yellow-100 text-yellow-800';
      case 'ui':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Changes</h1>
        <p className="text-gray-600">Track and analyze competitor changes</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>
          
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="feature">Feature</option>
            <option value="pricing">Pricing</option>
            <option value="ui">UI</option>
            <option value="other">Other</option>
          </select>

          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Severities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="date">Sort by Date</option>
            <option value="severity">Sort by Severity</option>
          </select>
        </div>
      </div>

      {/* Changes List */}
      <div className="space-y-4">
        {filteredChanges.map((change) => (
          <div
            key={change.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start space-x-4">
              <div className={`p-3 rounded-lg ${getChangeTypeColor(change.change_type)}`}>
                {getChangeTypeIcon(change.change_type)}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{change.competitor_name}</h3>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      change.severity === 'high' ? 'bg-red-100 text-red-800' :
                      change.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {change.severity}
                    </span>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getChangeTypeColor(change.change_type)}`}>
                      {change.change_type}
                    </span>
                  </div>
                </div>
                
                <p className="text-gray-700 mb-3">{change.description}</p>
                
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(change.detected_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredChanges.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Activity className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No changes found</h3>
          <p className="text-gray-600">
            {filterType !== 'all' || filterSeverity !== 'all'
              ? 'Try adjusting your filter criteria'
              : 'Start tracking competitors to see changes here'
            }
          </p>
        </div>
      )}

      {/* Summary Stats */}
      {dashboardData && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(dashboardData.change_types || {}).map(([type, count]) => (
              <div key={type} className="text-center">
                <p className="text-2xl font-bold text-gray-900">{count}</p>
                <p className="text-sm text-gray-600 capitalize">{type} changes</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Changes;


