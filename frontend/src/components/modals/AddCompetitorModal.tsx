import React, { useState } from 'react';
import { X, Plus, Globe } from 'lucide-react';
import type { Competitor } from '../../types';

interface AddCompetitorModalProps {
  show: boolean;
  setShow: (show: boolean) => void;
  addCompetitor: (competitor: Competitor) => void;
}

const AddCompetitorModal: React.FC<AddCompetitorModalProps> = ({ show, setShow, addCompetitor }) => {
  const [formData, setFormData] = useState({
    name: '',
    website: '',
    category: '',
    trackingUrls: ['']
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const competitor: Competitor = {
      id: Date.now().toString(), // Temporary ID
      name: formData.name,
      website: formData.website || undefined,
      category: formData.category || undefined,
      tracking_urls: formData.trackingUrls.filter(url => url.trim() !== ''),
      created_at: new Date(),
      status: 'active',
      last_updated: new Date()
    };

    addCompetitor(competitor);
    setShow(false);
    setFormData({ name: '', website: '', category: '', trackingUrls: [''] });
  };

  const addTrackingUrl = () => {
    setFormData(prev => ({
      ...prev,
      trackingUrls: [...prev.trackingUrls, '']
    }));
  };

  const removeTrackingUrl = (index: number) => {
    setFormData(prev => ({
      ...prev,
      trackingUrls: prev.trackingUrls.filter((_, i) => i !== index)
    }));
  };

  const updateTrackingUrl = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      trackingUrls: prev.trackingUrls.map((url, i) => i === index ? value : url)
    }));
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Add New Competitor</h2>
          <button
            onClick={() => setShow(false)}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Competitor Name *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., TechCorp, InnovateApp"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Website
              </label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select a category</option>
                <option value="SaaS">SaaS</option>
                <option value="Mobile">Mobile</option>
                <option value="E-commerce">E-commerce</option>
                <option value="Fintech">Fintech</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Education">Education</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          {/* Tracking URLs */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tracking URLs
            </label>
            <p className="text-sm text-gray-600 mb-4">
              Add specific URLs to monitor for changes (pricing pages, feature pages, etc.)
            </p>
            
            <div className="space-y-3">
              {formData.trackingUrls.map((url, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Globe className="w-4 h-4 text-gray-400" />
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => updateTrackingUrl(index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="https://example.com/pricing"
                  />
                  {formData.trackingUrls.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeTrackingUrl(index)}
                      className="px-2 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
              
              <button
                type="button"
                onClick={addTrackingUrl}
                className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                <Plus className="w-4 h-4" />
                <span>Add another URL</span>
              </button>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={() => setShow(false)}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Add Competitor
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddCompetitorModal;


