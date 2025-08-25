from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from enum import Enum

from database.mongo.manager import DatabaseManager
from database.mongo.schemas import Competitor, Snapshot, Change, Announcement, Report
from agent.competitor_tracking_agent import CompetitorTrackingAgent, WeeklyScheduler
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
        # In a real implementation, you'd add delete methods to DatabaseManager
        return {"message": f"Competitor {competitor_id} deleted successfully"}
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
    
    # Start background task
    if request and request.competitor_id:
        background_tasks.add_task(run_competitor_tracking, request.competitor_id)
    else:
        background_tasks.add_task(run_full_tracking, request.mode if request else "full")
    
    return {"message": "Tracking started", "status": tracking_status}

@router.post("/tracking/stop")
async def stop_tracking():
    """Stop current tracking process"""
    global tracking_status
    
    tracking_status.update({
        "status": TrackingStatus.IDLE,
        "current_task": None,
        "end_time": datetime.utcnow()
    })
    
    return {"message": "Tracking stopped", "status": tracking_status}

@router.post("/crawl")
async def crawl_competitor(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Crawl specific competitor or URLs"""
    try:
        if request.competitor_id:
            # Crawl specific competitor
            competitors = db.get_competitors()
            competitor = next((c for c in competitors if c["id"] == request.competitor_id), None)
            
            if not competitor:
                raise HTTPException(status_code=404, detail="Competitor not found")
            
            background_tasks.add_task(crawl_competitor_background, competitor)
            
            return {
                "message": f"Started crawling competitor: {competitor['name']}",
                "competitor_id": request.competitor_id,
                "urls_count": len(competitor.get("tracking_urls", []))
            }
        
        elif request.urls:
            # Crawl specific URLs
            background_tasks.add_task(crawl_urls_background, request.urls)
            
            return {
                "message": f"Started crawling {len(request.urls)} URLs",
                "urls": [str(url) for url in request.urls]
            }
        
        else:
            raise HTTPException(status_code=400, detail="Either competitor_id or urls must be provided")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start crawling: {str(e)}")

# ================================
# ANALYTICS & REPORTS ROUTES
# ================================

@router.get("/analytics/dashboard")
async def get_dashboard_data():
    """Get dashboard analytics data"""
    try:
        competitors = db.get_competitors()
        reports = db.get_reports()
        
        # Calculate metrics
        total_competitors = len(competitors)
        recent_reports = [r for r in reports if (datetime.utcnow() - r.get("delivered_at", datetime.utcnow())).days <= 7]
        
        # Get change statistics
        all_changes = []
        for comp in competitors:
            changes = db.get_changes(comp["id"])
            all_changes.extend(changes)
        
        # Recent changes (last 7 days)
        recent_changes = [
            c for c in all_changes 
            if (datetime.utcnow() - c.get("detected_at", datetime.utcnow())).days <= 7
        ]
        
        # Group changes by type
        change_types = {}
        for change in recent_changes:
            change_type = change.get("change_type", "other")
            change_types[change_type] = change_types.get(change_type, 0) + 1
        
        # Competitor activity
        competitor_activity = []
        for comp in competitors:
            changes = db.get_changes(comp["id"])
            snapshots = db.get_snapshots(comp["id"])
            
            recent_activity = len([
                c for c in changes 
                if (datetime.utcnow() - c.get("detected_at", datetime.utcnow())).days <= 7
            ])
            
            competitor_activity.append({
                "name": comp["name"],
                "category": comp.get("category", "Unknown"),
                "recent_changes": recent_activity,
                "total_snapshots": len(snapshots),
                "last_updated": snapshots[0].get("taken_at") if snapshots else None
            })
        
        return {
            "overview": {
                "total_competitors": total_competitors,
                "recent_reports": len(recent_reports),
                "recent_changes": len(recent_changes),
                "active_tracking": tracking_status["status"] == TrackingStatus.RUNNING
            },
            "change_types": change_types,
            "competitor_activity": competitor_activity,
            "tracking_status": tracking_status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")

@router.get("/reports")
async def get_reports(limit: int = Query(10, ge=1, le=50)):
    """Get recent reports"""
    try:
        reports = db.get_reports()
        
        # Sort by delivery date and limit
        sorted_reports = sorted(
            reports, 
            key=lambda x: x.get("delivered_at", datetime.utcnow()), 
            reverse=True
        )[:limit]
        
        return sorted_reports
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")

@router.get("/reports/{week}")
async def get_weekly_report(week: str):
    """Get specific weekly report"""
    try:
        reports = db.get_reports()
        report = next((r for r in reports if r.get("week") == week), None)
        
        if not report:
            raise HTTPException(status_code=404, detail=f"Report for week {week} not found")
        
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

@router.post("/reports/generate")
async def generate_report(background_tasks: BackgroundTasks):
    """Generate new weekly report"""
    try:
        background_tasks.add_task(generate_weekly_report_background)
        return {"message": "Report generation started"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start report generation: {str(e)}")

# ================================
# CHANGES & INSIGHTS ROUTES
# ================================

@router.get("/changes")
async def get_changes(
    competitor_id: Optional[str] = Query(None),
    change_type: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=200)
):
    """Get changes with filtering"""
    try:
        if competitor_id:
            changes = db.get_changes(competitor_id)
        else:
            # Get changes for all competitors
            competitors = db.get_competitors()
            changes = []
            for comp in competitors:
                comp_changes = db.get_changes(comp["id"])
                for change in comp_changes:
                    change["competitor_name"] = comp["name"]
                changes.extend(comp_changes)
        
        # Filter by date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        filtered_changes = [
            c for c in changes 
            if c.get("detected_at", datetime.utcnow()) >= cutoff_date
        ]
        
        # Filter by type if specified
        if change_type:
            filtered_changes = [
                c for c in filtered_changes 
                if c.get("change_type") == change_type
            ]
        
        # Sort by date and limit
        sorted_changes = sorted(
            filtered_changes,
            key=lambda x: x.get("detected_at", datetime.utcnow()),
            reverse=True
        )[:limit]
        
        return sorted_changes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch changes: {str(e)}")

@router.get("/insights/trending")
async def get_trending_insights():
    """Get trending insights and patterns"""
    try:
        # Get recent changes
        competitors = db.get_competitors()
        all_changes = []
        
        for comp in competitors:
            changes = db.get_changes(comp["id"])
            for change in changes:
                change["competitor_name"] = comp["name"]
                change["category"] = comp.get("category", "Unknown")
            all_changes.extend(changes)
        
        # Filter to last 30 days
        recent_changes = [
            c for c in all_changes 
            if (datetime.utcnow() - c.get("detected_at", datetime.utcnow())).days <= 30
        ]
        
        # Analyze trends
        category_trends = {}
        change_type_trends = {}
        
        for change in recent_changes:
            category = change.get("category", "Unknown")
            change_type = change.get("change_type", "other")
            
            category_trends[category] = category_trends.get(category, 0) + 1
            change_type_trends[change_type] = change_type_trends.get(change_type, 0) + 1
        
        # Most active competitors
        competitor_activity = {}
        for change in recent_changes:
            comp_name = change.get("competitor_name", "Unknown")
            competitor_activity[comp_name] = competitor_activity.get(comp_name, 0) + 1
        
        # Sort by activity
        top_competitors = sorted(
            competitor_activity.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "category_trends": category_trends,
            "change_type_trends": change_type_trends,
            "most_active_competitors": [{"name": name, "changes": count} for name, count in top_competitors],
            "total_changes_30d": len(recent_changes),
            "analysis_date": datetime.utcnow()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

# ================================
# BACKGROUND TASKS
# ================================

async def run_full_tracking(mode: str = "full"):
    """Background task for full tracking"""
    global tracking_status
    
    try:
        tracking_status["current_task"] = "Full competitor tracking"
        result = await scheduler.run_scheduled_tracking()
        
        tracking_status.update({
            "status": TrackingStatus.COMPLETED,
            "end_time": datetime.utcnow(),
            "progress": 100
        })
        
    except Exception as e:
        tracking_status.update({
            "status": TrackingStatus.ERROR,
            "end_time": datetime.utcnow(),
            "errors": [str(e)]
        })

async def run_competitor_tracking(competitor_id: str):
    """Background task for single competitor tracking"""
    global tracking_status
    
    try:
        tracking_status["current_task"] = f"Tracking competitor {competitor_id}"
        # Implement single competitor tracking logic
        await asyncio.sleep(2)  # Placeholder
        
        tracking_status.update({
            "status": TrackingStatus.COMPLETED,
            "end_time": datetime.utcnow(),
            "progress": 100
        })
        
    except Exception as e:
        tracking_status.update({
            "status": TrackingStatus.ERROR,
            "end_time": datetime.utcnow(),
            "errors": [str(e)]
        })

async def crawl_competitor_background(competitor: dict):
    """Background task for crawling specific competitor"""
    try:
        website_crawler = WebsiteCrawlTool()
        
        for url in competitor.get("tracking_urls", []):
            result = await website_crawler.run(str(url), max_pages=5)
            # Process and store results
            print(f"Crawled {url}: {len(result) if isinstance(result, dict) else 'Error'}")
            
    except Exception as e:
        print(f"Error crawling competitor {competitor['name']}: {str(e)}")

async def crawl_urls_background(urls: List[HttpUrl]):
    """Background task for crawling specific URLs"""
    try:
        website_crawler = WebsiteCrawlTool()
        
        for url in urls:
            result = await website_crawler.run(str(url), max_pages=3)
            print(f"Crawled {url}: {len(result) if isinstance(result, dict) else 'Error'}")
            
    except Exception as e:
        print(f"Error crawling URLs: {str(e)}")

async def generate_weekly_report_background():
    """Background task for generating weekly report"""
    try:
        result = await scheduler.run_scheduled_tracking()
        print(f"Weekly report generated: {result}")
        
    except Exception as e:
        print(f"Error generating weekly report: {str(e)}")

# ================================
# HEALTH CHECK
# ================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        competitors = db.get_competitors()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": "connected",
            "competitors_count": len(competitors),
            "tracking_status": tracking_status["status"]
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }