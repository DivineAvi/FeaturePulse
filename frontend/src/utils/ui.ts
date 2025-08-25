import type { ChangeSeverity, ChangeType, TrackingStatus } from '../types';

export const formatDate = (dateInput: Date | string): string => {
  return new Date(dateInput).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const getStatusColor = (status: TrackingStatus): string => {
  const colors: Record<TrackingStatus, string> = {
    idle: 'bg-gray-100 text-gray-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800'
  };
  return colors[status] || colors.idle;
};

export const getChangeTypeColor = (type: ChangeType): string => {
  const colors: Record<ChangeType, string> = {
    feature: 'bg-purple-100 text-purple-800',
    pricing: 'bg-yellow-100 text-yellow-800',
    ui: 'bg-blue-100 text-blue-800',
    other: 'bg-gray-100 text-gray-800'
  };
  return colors[type] || colors.other;
};

export const getSeverityColor = (severity: ChangeSeverity): string => {
  const colors: Record<ChangeSeverity, string> = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800'
  };
  return colors[severity] || colors.low;
};


