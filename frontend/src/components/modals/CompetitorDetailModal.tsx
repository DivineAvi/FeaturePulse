import React from 'react';
import { X, ExternalLink, Calendar, Activity, Tag } from 'lucide-react';
import type { Competitor, Change } from '../../types';

interface CompetitorDetailModalProps {
  competitor: Competitor | null;
  setCompetitor: (competitor: Competitor | null) => void;
  changes: Change[];
}

const CompetitorDetailModal: React.FC<CompetitorDetailModalProps> = ({ 
  competitor, 
  setCompetitor, 
  changes 
}) => {
  if (!competitor) return null;

  const competitorChanges = changes.filter(change => 
    change.competitor_name === competitor.name
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">{competitor.name}</h2>
          <button
            onClick={() => setCompetitor(null)}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Company Information</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-600">Name:</span>
                  <span className="text-sm text-gray-900">{competitor.name}</span>
                </div>
                
                {competitor.website && (
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-600">Website:</span>
                    <a
                      href={competitor.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                    >
                      <span>Visit</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
                
                {competitor.category && (
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-600">Category:</span>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      <Tag className="w-3 h-3 mr-1" />
                      {competitor.category}
                    </span>
                  </div>
                )}
                
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-600">Status:</span>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    competitor.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {competitor.status}
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Tracking Details</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Added:</span>
                  <span className="text-sm text-gray-900">
                    {new Date(competitor.created_at).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Last Updated:</span>
                  <span className="text-sm text-gray-900">
                    {competitor.last_updated ? new Date(competitor.last_updated).toLocaleDateString() : 'Never'}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Tracking URLs:</span>
                  <span className="text-sm text-gray-900">
                    {competitor.tracking_urls.length}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Tracking URLs */}
          {competitor.tracking_urls.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Tracking URLs</h3>
              <div className="space-y-2">
                {competitor.tracking_urls.map((url, index) => (
                  <div key={index} className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                    <ExternalLink className="w-4 h-4 text-gray-400" />
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-700 truncate"
                    >
                      {url}
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Changes */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Changes</h3>
            {competitorChanges.length > 0 ? (
              <div className="space-y-3">
                {competitorChanges.slice(0, 5).map((change) => (
                  <div key={change.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            change.change_type === 'feature' ? 'bg-green-100 text-green-800' :
                            change.change_type === 'pricing' ? 'bg-yellow-100 text-yellow-800' :
                            change.change_type === 'ui' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {change.change_type}
                          </span>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            change.severity === 'high' ? 'bg-red-100 text-red-800' :
                            change.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {change.severity}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mb-2">{change.description}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(change.detected_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No changes detected yet</p>
                <p className="text-sm text-gray-500">Start tracking to see changes here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompetitorDetailModal;


