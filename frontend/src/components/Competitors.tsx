import React from 'react';
import { Search, Plus, ExternalLink, Calendar, Tag, Activity } from 'lucide-react';
import type { Competitor } from '../types';

interface CompetitorsProps {
  competitors: Competitor[];
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  filterType: string;
  setFilterType: (type: string) => void;
  setShowAddModal: (show: boolean) => void;
  setSelectedCompetitor: (competitor: Competitor | null) => void;
}

const Competitors: React.FC<CompetitorsProps> = ({
  competitors,
  searchTerm,
  setSearchTerm,
  filterType,
  setFilterType,
  setShowAddModal,
  setSelectedCompetitor
}) => {
  const filteredCompetitors = competitors.filter(competitor => {
    const matchesSearch = competitor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         competitor.website?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         competitor.category?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterType === 'all' || competitor.category === filterType;
    
    return matchesSearch && matchesFilter;
  });

  const categories = Array.from(new Set(competitors.map(c => c.category).filter(Boolean)));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Competitors</h1>
          <p className="text-gray-600">Manage and monitor your competitors</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Competitor</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search competitors..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Categories</option>
          {categories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
      </div>

      {/* Competitors Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {filteredCompetitors.map((competitor) => (
          <div
            key={competitor.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedCompetitor(competitor)}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-1">{competitor.name}</h3>
                <div className="flex flex-wrap items-center gap-2">
                  {competitor.category && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      <Tag className="w-3 h-3 mr-1" />
                      {competitor.category}
                    </span>
                  )}
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    competitor.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {competitor.status}
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {competitor.website && (
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <ExternalLink className="w-4 h-4" />
                  <a
                    href={competitor.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-blue-600 truncate"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {competitor.website}
                  </a>
                </div>
              )}

              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Calendar className="w-4 h-4" />
                <span>Added {new Date(competitor.created_at).toLocaleDateString()}</span>
              </div>

              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Activity className="w-4 h-4" />
                <span>Last updated {competitor.last_updated ? new Date(competitor.last_updated).toLocaleDateString() : 'Never'}</span>
              </div>

              <div className="pt-3 border-t border-gray-100">
                <p className="text-sm text-gray-600">
                  {competitor.tracking_urls.length} tracking URL{competitor.tracking_urls.length !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredCompetitors.length === 0 && (
        <div className="text-center py-8 sm:py-12">
          <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-6 h-6 sm:w-8 sm:h-8 text-gray-400" />
          </div>
          <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-2">No competitors found</h3>
          <p className="text-sm sm:text-base text-gray-600 mb-4">
            {searchTerm || filterType !== 'all' 
              ? 'Try adjusting your search or filter criteria'
              : 'Get started by adding your first competitor'
            }
          </p>
          {!searchTerm && filterType === 'all' && (
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add Your First Competitor
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default Competitors;


