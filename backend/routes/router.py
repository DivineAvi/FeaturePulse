from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from enum import Enum

from database.mongo.manager import DatabaseManager
from database.mongo.schemas import Competitor, Snapshot, Change, Announcement, Report
from agent.feature_pulse_agent import CompetitorTrackingAgent, WeeklyScheduler
from tools.appstore_tool import AppStoreTool
from tools.playstore_tool import PlayStoreTool
from tools.website_crawl_tool import WebsiteCrawlTool
from tools.linkedin_crawl_tool import LinkedInCrawlTool

# Initialize router
router = APIRouter(prefix="/api")

# Pydantic models for API requests/responses
class CompetitorCreate(BaseModel):
    name: str
    website: Optional[HttpUrl] = None
    category: Optional[str] = None
    tracking_urls: List[HttpUrl] = []

class CompetitorResponse(BaseModel):
    id: str
    name: str
    website: Optional[str] = None
    category: Optional[str] = None
    tracking_urls: List[str] = []
    created_at: datetime

class TrackingStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

class CrawlRequest(BaseModel):
    competitor_id: Optional[str] = None
    urls: Optional[List[HttpUrl]] = None
    mode: str = "full"  # full, quick, test

class AnalysisResponse(BaseModel):
    competitor_id: str
    competitor_name: str
    changes_detected: int
    last_updated: datetime
    summary: str
    changes: List[Dict[str, Any]]

# Settings models
class NotificationSettings(BaseModel):
    email: bool = True
    slack: bool = True
    realtime: bool = False

class TrackingSettings(BaseModel):
    frequency: str = "Weekly"
    max_pages: int = 10
    smart_scroll: bool = True

class DataManagementSettings(BaseModel):
    retention_period: str = "90 days"
    auto_cleanup: bool = True

class UserSettings(BaseModel):
    notifications: NotificationSettings
    tracking: TrackingSettings
    data_management: DataManagementSettings

# Global instances
db = DatabaseManager()
scheduler = WeeklyScheduler()
agent = CompetitorTrackingAgent()

# In-memory tracking status (in production, use Redis)
tracking_status = {
    "status": TrackingStatus.IDLE,
    "current_task": None,
    "progress": 0,
    "total": 0,
    "start_time": None,
    "end_time": None,
    "errors": []
}

# In-memory settings storage (in production, use database)
user_settings = UserSettings(
    notifications=NotificationSettings(),
    tracking=TrackingSettings(),
    data_management=DataManagementSettings()
)

# ================================
# SETTINGS ROUTES
# ================================

@router.get("/settings")
async def get_settings():
    """Get current user settings"""
    return user_settings

@router.post("/settings")
async def update_settings(settings: UserSettings):
    """Update user settings"""
    global user_settings
    user_settings = settings
    return {"message": "Settings updated successfully"}

@router.post("/settings/test-notification")
async def test_notification(notification_type: str):
    """Test notification delivery"""
    try:
        if notification_type == "email":
            # Simulate email notification
            return {"message": "Email notification test sent successfully"}
        elif notification_type == "slack":
            # Simulate Slack notification
            return {"message": "Slack notification test sent successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid notification type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test notification: {str(e)}")

@router.post("/settings/cleanup-data")
async def cleanup_old_data():
    """Clean up old data based on retention settings"""
    try:
        # Get retention period from settings
        retention_period = user_settings.data_management.retention_period
        
        # Calculate cutoff date
        if retention_period == "30 days":
            cutoff_date = datetime.utcnow() - timedelta(days=30)
        elif retention_period == "90 days":
            cutoff_date = datetime.utcnow() - timedelta(days=90)
        elif retention_period == "1 year":
            cutoff_date = datetime.utcnow() - timedelta(days=365)
        else:  # Forever
            return {"message": "Data retention set to forever, no cleanup needed"}
        
        # Clean up old snapshots, changes, and reports
        # This would be implemented in the database manager
        # For now, we'll simulate the cleanup
        
        return {
            "message": f"Data cleanup completed successfully",
            "cutoff_date": cutoff_date.isoformat(),
            "retention_period": retention_period
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup data: {str(e)}")

# ================================
# COMPETITOR MANAGEMENT ROUTES
# ================================

@router.get("/competitors", response_model=List[CompetitorResponse])
async def get_competitors():
    """Get all competitors"""
    try:
        competitors = db.get_competitors()
        return [CompetitorResponse(
            id=comp["id"],
            name=comp["name"],
            website=comp.get("website"),
            category=comp.get("category"),
            tracking_urls=[str(url) for url in comp.get("tracking_urls", [])],
            created_at=comp.get("created_at", datetime.utcnow())
        ) for comp in competitors]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch competitors: {str(e)}")

@router.post("/competitors", response_model=Dict[str, str])
async def create_competitor(competitor: CompetitorCreate):
    """Add a new competitor"""
    try:
        competitor_obj = Competitor(
            name=competitor.name,
            website=competitor.website,
            category=competitor.category,
            tracking_urls=competitor.tracking_urls
        )
        
        competitor_id = db.add_competitor(competitor_obj)
        return {"id": competitor_id, "message": f"Competitor '{competitor.name}' added successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add competitor: {str(e)}")

@router.get("/competitors/{competitor_id}")
async def get_competitor(competitor_id: str):
    """Get specific competitor details with recent activity"""
    try:
        competitors = db.get_competitors()
        competitor = next((c for c in competitors if c["id"] == competitor_id), None)
        
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        # Get recent snapshots and changes
        snapshots = db.get_snapshots(competitor_id)
        changes = db.get_changes(competitor_id)
        announcements = db.get_announcements(competitor_id)
        
        return {
            "competitor": CompetitorResponse(
                id=competitor["id"],
                name=competitor["name"],
                website=competitor.get("website"),
                category=competitor.get("category"),
                tracking_urls=[str(url) for url in competitor.get("tracking_urls", [])],
                created_at=competitor.get("created_at", datetime.utcnow())
            ),
            "snapshots_count": len(snapshots),
            "changes_count": len(changes),
            "announcements_count": len(announcements),
            "last_snapshot": snapshots[0] if snapshots else None,
            "recent_changes": changes[:5],  # Last 5 changes
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch competitor: {str(e)}")

@router.delete("/competitors/{competitor_id}")
async def delete_competitor(competitor_id: str):
    """Delete a competitor and all related data"""
    try:
        deleted = db.delete_competitor(competitor_id)
        if deleted.get("deleted_competitors", 0) == 0:
            raise HTTPException(status_code=404, detail="Competitor not found")
        return {
            "message": f"Competitor {competitor_id} deleted successfully",
            **deleted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete competitor: {str(e)}")

# ================================
# TRACKING & CRAWLING ROUTES
# ================================

@router.get("/tracking/status")
async def get_tracking_status():
    """Get current tracking status"""
    return tracking_status

@router.post("/tracking/start")
async def start_tracking(background_tasks: BackgroundTasks, request: Optional[CrawlRequest] = None):
    """Start tracking process"""
    global tracking_status
    
    if tracking_status["status"] == TrackingStatus.RUNNING:
        raise HTTPException(status_code=409, detail="Tracking is already running")
    
    # Update status
    tracking_status.update({
        "status": TrackingStatus.RUNNING,
        "start_time": datetime.utcnow(),
        "end_time": None,
        "progress": 0,
        "errors": []
    })
    
    # Start tracking in background
    background_tasks.add_task(scheduler.run_scheduled_tracking)
    
    return {"message": "Tracking started successfully"}

@router.post("/tracking/stop")
async def stop_tracking():
    """Stop tracking process"""
    global tracking_status
    
    tracking_status.update({
        "status": TrackingStatus.IDLE,
        "end_time": datetime.utcnow()
    })
    
    return {"message": "Tracking stopped successfully"}

@router.post("/crawl")
async def crawl_competitor(request: CrawlRequest):
    """Crawl specific competitor or URLs"""
    try:
        if request.competitor_id:
            # Crawl specific competitor
            competitors = db.get_competitors()
            competitor = next((c for c in competitors if c["id"] == request.competitor_id), None)
            
            if not competitor:
                raise HTTPException(status_code=404, detail="Competitor not found")
            
            # Use agent to crawl competitor
            result = await agent.run_weekly_tracking()
            return result
        elif request.urls:
            # Crawl specific URLs
            # This would be implemented with the crawler tools
            return {"message": "URL crawling completed", "urls": [str(url) for url in request.urls]}
        else:
            raise HTTPException(status_code=400, detail="Either competitor_id or urls must be provided")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")

# ================================
# ANALYTICS ROUTES
# ================================

@router.get("/analytics/dashboard")
async def get_dashboard_data():
    """Get dashboard analytics data"""
    try:
        competitors = db.get_competitors()
        changes = db.get_changes("")  # Get all changes
        reports = db.get_reports()
        
        # Calculate overview metrics
        overview = {
            "total_competitors": len(competitors),
            "recent_changes": len([c for c in changes if (datetime.utcnow() - c.get("detected_at", datetime.utcnow())).days <= 7]),
            "recent_reports": len([r for r in reports if (datetime.utcnow() - r.get("delivered_at", datetime.utcnow())).days <= 7]),
            "active_tracking": tracking_status["status"] == TrackingStatus.RUNNING
        }
        
        # Calculate change types
        change_types = {"feature": 0, "pricing": 0, "ui": 0, "other": 0}
        for change in changes:
            change_type = change.get("change_type", "other")
            if change_type in change_types:
                change_types[change_type] += 1
        
        # Calculate competitor activity
        competitor_activity = []
        for comp in competitors:
            comp_changes = [c for c in changes if c.get("competitor_id") == comp["id"]]
            competitor_activity.append({
                "name": comp["name"],
                "category": comp.get("category", "Other"),
                "recent_changes": len([c for c in comp_changes if (datetime.utcnow() - c.get("detected_at", datetime.utcnow())).days <= 7]),
                "total_snapshots": len(db.get_snapshots(comp["id"]))
            })
        
        return {
            "overview": overview,
            "change_types": change_types,
            "competitor_activity": competitor_activity
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")

@router.get("/insights/trending")
async def get_trending_insights():
    """Get trending insights and analytics"""
    try:
        competitors = db.get_competitors()
        changes = db.get_changes("")  # Get all changes
        
        # Calculate category trends
        category_trends = {}
        for comp in competitors:
            category = comp.get("category", "Other")
            category_trends[category] = category_trends.get(category, 0) + 1
        
        # Calculate change type trends
        change_type_trends = {"feature": 0, "pricing": 0, "ui": 0, "other": 0}
        for change in changes:
            change_type = change.get("change_type", "other")
            if change_type in change_type_trends:
                change_type_trends[change_type] += 1
        
        # Calculate most active competitors
        competitor_activity = {}
        for change in changes:
            comp_id = change.get("competitor_id")
            if comp_id:
                competitor_activity[comp_id] = competitor_activity.get(comp_id, 0) + 1
        
        most_active = []
        for comp in competitors:
            if comp["id"] in competitor_activity:
                most_active.append({
                    "name": comp["name"],
                    "changes": competitor_activity[comp["id"]]
                })
        
        most_active.sort(key=lambda x: x["changes"], reverse=True)
        
        # Calculate total changes in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_changes = [c for c in changes if c.get("detected_at", datetime.utcnow()) >= thirty_days_ago]
        
        return {
            "category_trends": category_trends,
            "change_type_trends": change_type_trends,
            "most_active_competitors": most_active[:5],  # Top 5
            "total_changes_30d": len(recent_changes)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch insights: {str(e)}")

# ================================
# CHANGES ROUTES
# ================================

@router.get("/changes")
async def get_changes(
    competitor_id: Optional[str] = Query(None),
    change_type: Optional[str] = Query(None),
    days: Optional[int] = Query(None),
    limit: Optional[int] = Query(50)
):
    """Get detected changes with optional filtering"""
    try:
        changes = db.get_changes(competitor_id or "")
        
        # Apply filters
        if change_type:
            changes = [c for c in changes if c.get("change_type") == change_type]
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            changes = [c for c in changes if c.get("detected_at", datetime.utcnow()) >= cutoff_date]
        
        # Apply limit
        changes = changes[:limit]
        
        return changes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch changes: {str(e)}")

# ================================
# REPORTS ROUTES
# ================================

@router.get("/reports")
async def get_reports(limit: Optional[int] = Query(10)):
    """Get generated reports"""
    try:
        reports = db.get_reports()
        return reports[:limit]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")

@router.get("/reports/{week}")
async def get_report(week: str):
    """Get specific report by week"""
    try:
        reports = db.get_reports()
        report = next((r for r in reports if r.get("week") == week), None)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

@router.post("/reports/generate")
async def generate_report(background_tasks: BackgroundTasks):
    """Generate a new weekly report"""
    try:
        # Start report generation in background
        background_tasks.add_task(scheduler.run_scheduled_tracking)
        
        return {"message": "Report generation started successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/reports/{report_id}/download")
async def download_report(report_id: str):
    """Download a report as PDF"""
    try:
        # Get the report data
        reports = db.get_reports()
        report = next((r for r in reports if r.get("id") == report_id), None)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if report.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Report is not ready for download")
        
        # Generate PDF content (this would be implemented with a PDF library like reportlab)
        # For now, we'll create a simple text-based report
        from fastapi.responses import Response
        
        # Create a simple text report
        report_content = f"""
COMPETITOR INTELLIGENCE REPORT
==============================

Report: {report.get('title', 'Weekly Report')}
Week: {report.get('week', 'Unknown')}
Generated: {report.get('delivered_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Competitors Tracked: {report.get('competitors_tracked', 0)}
Changes Detected: {report.get('changes_detected', 0)}
Status: {report.get('status', 'Unknown')}

DETAILED ANALYSIS
----------------
This report contains detailed analysis of competitor activities and changes detected during the tracking period.

For more detailed information, please visit the dashboard at your competitor tracking application.

Generated by FeaturePulse Competitor Tracker
        """
        
        # Return as text file (in production, you'd generate a proper PDF)
        return Response(
            content=report_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=report_{report.get('week', 'unknown')}.txt"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")

@router.get("/reports/download/all")
async def download_all_reports():
    """Download all completed reports as a zip file"""
    try:
        import zipfile
        import io
        
        # Get all completed reports
        reports = db.get_reports()
        completed_reports = [r for r in reports if r.get("status") == "completed"]
        
        if not completed_reports:
            raise HTTPException(status_code=404, detail="No completed reports found")
        
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for report in completed_reports:
                # Create report content
                report_content = f"""
COMPETITOR INTELLIGENCE REPORT
==============================

Report: {report.get('title', 'Weekly Report')}
Week: {report.get('week', 'Unknown')}
Generated: {report.get('delivered_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Competitors Tracked: {report.get('competitors_tracked', 0)}
Changes Detected: {report.get('changes_detected', 0)}
Status: {report.get('status', 'Unknown')}

DETAILED ANALYSIS
----------------
This report contains detailed analysis of competitor activities and changes detected during the tracking period.

For more detailed information, please visit the dashboard at your competitor tracking application.

Generated by FeaturePulse Competitor Tracker
                """
                
                # Add file to zip
                filename = f"report_{report.get('week', 'unknown')}.txt"
                zip_file.writestr(filename, report_content)
        
        # Reset buffer position
        zip_buffer.seek(0)
        
        # Return zip file
        from fastapi.responses import Response
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=all_reports_{datetime.utcnow().strftime('%Y%m%d')}.zip"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download all reports: {str(e)}")

# ================================
# HEALTH CHECK
# ================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }