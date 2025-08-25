export type TrackingStatus = 'idle' | 'running' | 'completed' | 'error';
export type CompetitorStatus = 'active' | 'inactive';
export type CompetitorCategory = 'SaaS' | 'Mobile' | 'E-commerce' | 'Fintech' | 'Other';
export type ChangeType = 'feature' | 'pricing' | 'ui' | 'other';
export type ChangeSeverity = 'high' | 'medium' | 'low';
export type ReportStatus = 'completed' | 'pending' | 'error';
export type TabName = 'dashboard' | 'competitors' | 'changes' | 'reports' | 'analytics' | 'settings';

export interface Competitor {
  id: string;
  name: string;
  website?: string;
  category?: string;
  tracking_urls: string[];
  created_at: Date;
  status?: CompetitorStatus;
  last_updated?: Date;
}

export interface DashboardOverview {
  total_competitors: number;
  recent_changes: number;
  recent_reports: number;
  active_tracking: boolean;
}

export interface ChangeTypes {
  feature: number;
  pricing: number;
  ui: number;
  other: number;
}

export interface CompetitorActivity {
  name: string;
  category: CompetitorCategory;
  recent_changes: number;
  total_snapshots: number;
}

export interface DashboardData {
  overview: DashboardOverview;
  change_types: ChangeTypes;
  competitor_activity: CompetitorActivity[];
}

export interface Change {
  id: string;
  competitor_name?: string;
  change_type: string;
  description?: string;
  summary?: string;
  detected_at: Date;
  severity?: ChangeSeverity;
  url?: string;
}

export interface Report {
  id: string;
  week: string;
  title: string;
  delivered_at: Date;
  status: ReportStatus;
  competitors_tracked: number;
  changes_detected: number;
}

export interface CategoryTrends {
  [key: string]: number;
}

export interface MostActiveCompetitor {
  name: string;
  changes: number;
}

export interface Insights {
  category_trends: CategoryTrends;
  change_type_trends: ChangeTypes;
  most_active_competitors: MostActiveCompetitor[];
  total_changes_30d: number;
}

export interface TrackingStatusState {
  status: TrackingStatus;
}

export interface AddCompetitorFormData {
  name: string;
  website: string;
  category: CompetitorCategory;
  tracking_urls: string[];
}


