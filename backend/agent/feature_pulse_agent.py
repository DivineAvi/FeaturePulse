import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass
import json

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Import your existing classes
from llm.manager import LLM
from database.mongo.manager import DatabaseManager
from database.mongo.schemas import Competitor, Snapshot, Change, Announcement, Report
from tools.appstore_tool import AppStoreTool
from tools.playstore_tool import PlayStoreTool
from tools.linkedin_crawl_tool import LinkedInCrawlTool
from tools.website_crawl_tool import WebsiteCrawlTool
from integration.slack import SlackWebhook
from utils.utils import hash_content, diff_text, detect_changes

# ================================
# STATE DEFINITION
# ================================
class AgentState(TypedDict):
    # Current processing stage
    stage: str
    
    # Competitor data
    competitors: List[Dict[str, Any]]
    current_competitor: Optional[Dict[str, Any]]
    
    # Monitoring results
    website_snapshots: List[Dict[str, Any]]
    app_updates: List[Dict[str, Any]]
    social_posts: List[Dict[str, Any]]
    
    # Change detection
    detected_changes: List[Dict[str, Any]]
    
    # AI Analysis
    analysis_results: List[Dict[str, Any]]
    weekly_summary: Optional[str]
    
    # Delivery status
    delivery_status: Dict[str, Any]
    
    # Error handling
    errors: List[str]
    retry_count: int

# ================================
# TOOLS SETUP
# ================================
class CompetitorTrackingTools:
    def __init__(self):
        self.db = DatabaseManager()
        self.llm = LLM
        self.slack = SlackWebhook()
        
        # Initialize tools
        self.website_crawler = WebsiteCrawlTool()
        self.appstore_tool = AppStoreTool()
        self.playstore_tool = PlayStoreTool()
        self.linkedin_crawler = LinkedInCrawlTool()
        
        # Available tools for LangGraph
        self.tools = [
            self.website_crawler.definition,
            self.appstore_tool.definition,
            self.playstore_tool.definition,
            self.linkedin_crawler.definition
        ]

    async def crawl_website(self, url: str, max_pages: int = 5) -> Dict[str, Any]:
        """Crawl competitor website and return content"""
        try:
            result = await self.website_crawler.run(
                url=url, 
                max_pages=max_pages, 
                scroll=True, 
                smart_scroll=True
            )
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_app_info(self, app_id: str, store_type: str) -> Dict[str, Any]:
        """Get app store information"""
        try:
            if store_type == "appstore":
                result = await self.appstore_tool.run(app_id)
            else:  # playstore
                result = await self.playstore_tool.run(app_id)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def crawl_social(self, social_url: str) -> Dict[str, Any]:
        """Crawl social media posts"""
        try:
            if "linkedin" in social_url:
                result = await self.linkedin_crawler.run(social_url, max_posts=10)
            else:
                # For other social platforms, use website crawler
                result = await self.website_crawler.run(social_url, max_pages=1, scroll=True)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

# ================================
# AGENT NODES
# ================================
class CompetitorTrackingAgent:
    def __init__(self):
        self.tools = CompetitorTrackingTools()
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("fetch_competitors", self.fetch_competitors)
        workflow.add_node("monitor_websites", self.monitor_websites)
        workflow.add_node("monitor_apps", self.monitor_apps)
        workflow.add_node("monitor_social", self.monitor_social)
        workflow.add_node("detect_changes", self.detect_changes)
        workflow.add_node("analyze_changes", self.analyze_changes)
        workflow.add_node("generate_summary", self.generate_summary)
        workflow.add_node("deliver_report", self.deliver_report)
        workflow.add_node("handle_errors", self.handle_errors)
        
        # Define the flow
        workflow.add_edge(START, "fetch_competitors")
        workflow.add_edge("fetch_competitors", "monitor_websites")
        workflow.add_edge("monitor_websites", "monitor_apps")
        workflow.add_edge("monitor_apps", "monitor_social")
        workflow.add_edge("monitor_social", "detect_changes")
        workflow.add_edge("detect_changes", "analyze_changes")
        workflow.add_edge("analyze_changes", "generate_summary")
        workflow.add_edge("generate_summary", "deliver_report")
        workflow.add_edge("deliver_report", END)
        
        # Error handling edges
        workflow.add_edge("handle_errors", END)
        
        return workflow.compile(checkpointer=self.memory)

    async def fetch_competitors(self, state: AgentState) -> AgentState:
        """Fetch all competitors from database"""
        try:
            competitors = self.tools.db.get_competitors()
            state["competitors"] = competitors
            state["stage"] = "competitors_fetched"
            print(f"✅ Fetched {len(competitors)} competitors")
            return state
        except Exception as e:
            state["errors"].append(f"Failed to fetch competitors: {str(e)}")
            state["stage"] = "error"
            return state

    async def monitor_websites(self, state: AgentState) -> AgentState:
        """Monitor competitor websites for changes"""
        website_snapshots = []
        
        for competitor in state["competitors"]:
            state["current_competitor"] = competitor
            
            try:
                # Crawl main website
                if competitor.get("website"):
                    result = await self.tools.crawl_website(
                        competitor["website"], 
                        max_pages=10
                    )
                    
                    if result["success"]:
                        # Store snapshot
                        for url, content in result["data"].items():
                            snapshot = {
                                "competitor_id": competitor["id"],
                                "url": url,
                                "content": content,
                                "content_hash": hash_content(content),
                                "timestamp": datetime.utcnow()
                            }
                            website_snapshots.append(snapshot)
                
                # Crawl specific tracking URLs
                for tracking_url in competitor.get("tracking_urls", []):
                    result = await self.tools.crawl_website(str(tracking_url), max_pages=3)
                    
                    if result["success"]:
                        for url, content in result["data"].items():
                            snapshot = {
                                "competitor_id": competitor["id"],
                                "url": url,
                                "content": content,
                                "content_hash": hash_content(content),
                                "timestamp": datetime.utcnow()
                            }
                            website_snapshots.append(snapshot)
                            
            except Exception as e:
                state["errors"].append(f"Website monitoring failed for {competitor['name']}: {str(e)}")
        
        state["website_snapshots"] = website_snapshots
        state["stage"] = "websites_monitored"
        print(f"✅ Monitored websites, captured {len(website_snapshots)} snapshots")
        return state

    async def monitor_apps(self, state: AgentState) -> AgentState:
        """Monitor app store updates"""
        app_updates = []
        
        for competitor in state["competitors"]:
            try:
                # Check if competitor has app store info in tracking URLs
                for tracking_url in competitor.get("tracking_urls", []):
                    url_str = str(tracking_url)
                    
                    if "apps.apple.com" in url_str:
                        # Extract app ID from Apple App Store URL
                        app_id = url_str.split("/id")[-1].split("?")[0] if "/id" in url_str else None
                        if app_id:
                            result = await self.tools.get_app_info(app_id, "appstore")
                            if result["success"] and not result["data"].get("error"):
                                app_updates.append({
                                    "competitor_id": competitor["id"],
                                    "store": "appstore",
                                    "app_id": app_id,
                                    "data": result["data"],
                                    "timestamp": datetime.utcnow()
                                })
                    
                    elif "play.google.com" in url_str:
                        # Extract package name from Google Play Store URL
                        package_name = url_str.split("/details?id=")[-1].split("&")[0] if "/details?id=" in url_str else None
                        if package_name:
                            result = await self.tools.get_app_info(package_name, "playstore")
                            if result["success"] and not result["data"].get("error"):
                                app_updates.append({
                                    "competitor_id": competitor["id"],
                                    "store": "playstore",
                                    "package_name": package_name,
                                    "data": result["data"],
                                    "timestamp": datetime.utcnow()
                                })
            
            except Exception as e:
                state["errors"].append(f"App monitoring failed for {competitor['name']}: {str(e)}")
        
        state["app_updates"] = app_updates
        state["stage"] = "apps_monitored"
        print(f"✅ Monitored apps, found {len(app_updates)} updates")
        return state

    async def monitor_social(self, state: AgentState) -> AgentState:
        """Monitor social media announcements"""
        social_posts = []
        
        for competitor in state["competitors"]:
            try:
                # Look for social media URLs in tracking URLs
                for tracking_url in competitor.get("tracking_urls", []):
                    url_str = str(tracking_url)
                    
                    if any(platform in url_str for platform in ["linkedin.com", "twitter.com", "x.com"]):
                        result = await self.tools.crawl_social(url_str)
                        if result["success"]:
                            social_posts.append({
                                "competitor_id": competitor["id"],
                                "platform": "linkedin" if "linkedin" in url_str else "twitter",
                                "url": url_str,
                                "data": result["data"],
                                "timestamp": datetime.utcnow()
                            })
            
            except Exception as e:
                state["errors"].append(f"Social monitoring failed for {competitor['name']}: {str(e)}")
        
        state["social_posts"] = social_posts
        state["stage"] = "social_monitored"
        print(f"✅ Monitored social media, found {len(social_posts)} posts")
        return state

    async def detect_changes(self, state: AgentState) -> AgentState:
        """Detect changes by comparing with previous snapshots"""
        detected_changes = []
        
        # Check website changes
        for snapshot in state["website_snapshots"]:
            try:
                # Get previous snapshots for this URL
                previous_snapshots = self.tools.db.get_snapshots(snapshot["competitor_id"])
                
                # Find previous snapshot for same URL
                previous_snapshot = None
                for prev in previous_snapshots:
                    if prev["url"] == snapshot["url"]:
                        previous_snapshot = prev
                        break
                
                if previous_snapshot:
                    # Compare content hashes
                    if previous_snapshot["content_hash"] != snapshot["content_hash"]:
                        change_analysis = detect_changes(
                            previous_snapshot["raw_text"], 
                            snapshot["content"]
                        )
                        
                        detected_changes.append({
                            "competitor_id": snapshot["competitor_id"],
                            "change_type": "website",
                            "url": snapshot["url"],
                            "change_details": change_analysis,
                            "timestamp": datetime.utcnow()
                        })
                
                # Save new snapshot to database
                snapshot_obj = Snapshot(
                    competitor_id=snapshot["competitor_id"],
                    url=snapshot["url"],
                    content_hash=snapshot["content_hash"],
                    raw_text=snapshot["content"],
                    taken_at=snapshot["timestamp"]
                )
                self.tools.db.add_snapshot(snapshot_obj)
                
            except Exception as e:
                state["errors"].append(f"Change detection failed for snapshot: {str(e)}")
        
        # Check app changes
        for app_update in state["app_updates"]:
            try:
                # Compare with previous app version data (simplified)
                # In a real implementation, you'd store and compare app versions
                
                # Get the app store URL from tracking URLs
                competitor = next(
                    (c for c in state["competitors"] if c["id"] == app_update["competitor_id"]), 
                    {}
                )
                
                app_url = ""
                for tracking_url in competitor.get("tracking_urls", []):
                    url_str = str(tracking_url)
                    if (app_update["store"] == "appstore" and "apps.apple.com" in url_str) or \
                       (app_update["store"] == "playstore" and "play.google.com" in url_str):
                        app_url = url_str
                        break
                
                detected_changes.append({
                    "competitor_id": app_update["competitor_id"],
                    "change_type": "app",
                    "url": app_url,
                    "store": app_update["store"],
                    "data": app_update["data"],
                    "timestamp": app_update["timestamp"]
                })
            except Exception as e:
                state["errors"].append(f"App change detection failed: {str(e)}")
        
        state["detected_changes"] = detected_changes
        state["stage"] = "changes_detected"
        print(f"✅ Detected {len(detected_changes)} changes")
        return state

    async def analyze_changes(self, state: AgentState) -> AgentState:
        """Use AI to analyze and categorize changes"""
        analysis_results = []
        
        for change in state["detected_changes"]:
            try:
                # Create competitor context
                competitor = next(
                    (c for c in state["competitors"] if c["id"] == change["competitor_id"]), 
                    {}
                )
                
                # Prepare analysis prompt
                if change["change_type"] == "website":
                    url_display = change.get('url', '') or 'N/A'
                    analysis_prompt = f"""
                    Analyze this website change for competitor {competitor.get('name', 'Unknown')}:
                    
                    URL: {url_display}
                    Changes detected:
                    {change['change_details'].get('diff', '')}
                    
                    Provide a detailed analysis in this format:
                    1. **Change Type**: Categorize as feature, pricing, ui, marketing, or other
                    2. **What Changed**: Specific details of what was modified (e.g., "Price increased from $9.99 to $12.99", "New feature X added", "UI redesigned")
                    3. **Business Impact**: Potential impact on market positioning, customer acquisition, or competitive advantage
                    4. **Strategic Insights**: What this change suggests about their strategy or market direction
                    
                    Be specific about numbers, features, and concrete changes when possible.
                    """
                
                elif change["change_type"] == "app":
                    app_data = change["data"]
                    app_url = change.get('url', '') or 'N/A'
                    analysis_prompt = f"""
                    Analyze this app update for competitor {competitor.get('name', 'Unknown')}:
                    
                    App: {app_data.get('title', 'Unknown')}
                    Version: {app_data.get('version', 'Unknown')}
                    Store URL: {app_url}
                    Release Notes: {app_data.get('release_notes', 'No notes')}
                    Description: {app_data.get('description', 'No description')[:500]}
                    
                    Provide a detailed analysis in this format:
                    1. **Change Type**: Categorize as feature, pricing, ui, bugfix, or other
                    2. **What Changed**: Specific new features, UI updates, or changes (e.g., "Added dark mode", "New payment integration", "Performance improvements")
                    3. **Business Impact**: How this update affects user experience, market positioning, or competitive advantage
                    4. **Strategic Insights**: What this update reveals about their product roadmap or market strategy
                    
                    Extract specific details from release notes and description.
                    """
                
                # Get AI analysis
                result = self.tools.llm.chat(
                    question=analysis_prompt,
                    system_prompt="You are a senior competitive intelligence analyst with expertise in product strategy and market analysis. Your role is to provide detailed, actionable insights about competitor changes. Focus on extracting specific details like pricing changes, feature additions, UI modifications, and strategic implications. Be precise with numbers, dates, and concrete changes. Structure your analysis to help product teams make informed strategic decisions."
                )
                
                # Build detailed payload per change for richer reporting later
                detailed_payload = {
                    "competitor_id": change["competitor_id"],
                    "competitor_name": competitor.get("name", "Unknown"),
                    "change_type": change["change_type"],
                    "url": change.get("url", "") or "N/A",
                    "timestamp": change["timestamp"],
                    "analysis": result["reply"],
                }
                if change["change_type"] == "website":
                    detailed_payload["details"] = {
                        "diff": change.get("change_details", {}).get("diff", ""),
                        "previous_hash": change.get("change_details", {}).get("old_hash", ""),
                        "new_hash": change.get("change_details", {}).get("new_hash", ""),
                    }
                elif change["change_type"] == "app":
                    app_data = change["data"]
                    detailed_payload["details"] = {
                        "store": change.get("store", ""),
                        "title": app_data.get("title", "Unknown"),
                        "version": app_data.get("version", "Unknown"),
                        "release_notes": app_data.get("release_notes", ""),
                        "description": (app_data.get("description", "") or "")[:1000],
                    }
                analysis_results.append(detailed_payload)
                
                # Store change in database
                # Only include URL if it's a valid non-empty string
                change_url = change.get("url", "")
                if not change_url or change_url.strip() == "":
                    # Don't include URL field at all if it's empty
                    change_obj = Change(
                        competitor_id=change["competitor_id"],
                        change_type="other",  # Will be updated based on AI analysis
                        summary=result["reply"][:500],
                        previous_hash=change.get("change_details", {}).get("old_hash", ""),
                        new_hash=change.get("change_details", {}).get("new_hash", "")
                    )
                else:
                    change_obj = Change(
                        competitor_id=change["competitor_id"],
                        url=change_url,
                        change_type="other",  # Will be updated based on AI analysis
                        summary=result["reply"][:500],
                        previous_hash=change.get("change_details", {}).get("old_hash", ""),
                        new_hash=change.get("change_details", {}).get("new_hash", "")
                    )
                self.tools.db.add_change(change_obj)
                
            except Exception as e:
                state["errors"].append(f"Change analysis failed: {str(e)}")
        
        state["analysis_results"] = analysis_results
        state["stage"] = "changes_analyzed"
        print(f"✅ Analyzed {len(analysis_results)} changes")
        return state

    async def generate_summary(self, state: AgentState) -> AgentState:
        """Generate weekly summary report"""
        try:
            # Prepare summary data (ensure detailed data per change for reporting)
            competitor_summaries = {}
            for analysis in state["analysis_results"]:
                comp_id = analysis["competitor_id"]
                comp_name = analysis["competitor_name"]
                
                if comp_id not in competitor_summaries:
                    competitor_summaries[comp_id] = {
                        "name": comp_name,
                        "changes": []
                    }
                
                competitor_summaries[comp_id]["changes"].append({
                    "type": analysis["change_type"],
                    "competitor_name": analysis.get("competitor_name", comp_name),
                    "url": analysis.get("url", "N/A"),
                    "timestamp": str(analysis.get("timestamp", "")),
                    "details": analysis.get("details", {}),
                    "analysis": analysis.get("analysis", ""),
                })
            
            # Generate comprehensive summary
            current_week = datetime.now().strftime("%Y-W%U")
            
            summary_prompt = f"""
            Generate a comprehensive weekly competitor intelligence report for week {current_week}.
            
            Input (JSON):
            {json.dumps(competitor_summaries, indent=2)}
            
            Produce a structured Markdown report organized by COMPETITOR:
            
            ## Executive Summary
            Brief overview of key competitive themes and trends across all competitors.
            
            ## Competitor Analysis
            
            For each competitor, create a section like this:
            
            ### [Competitor Name]
            
            **Overview**: Brief summary of their recent activity and strategic direction.
            
            **Changes Detected**:
            - **Change Type**: [feature/pricing/ui/marketing/other]
            - **What Changed**: [Specific details - e.g., "Price increased from $9.99 to $12.99", "Added new AI feature"]
            - **URL**: [Link if available]
            - **Timestamp**: [When detected]
            - **Business Impact**: [How this affects market positioning]
            - **Strategic Insights**: [What this reveals about their strategy]
            
            **Key Insights**:
            - [Strategic implications for this competitor]
            - [Market positioning analysis]
            - [Potential competitive threats or opportunities]
            
            ## Overall Market Insights
            Cross-competitor analysis and market trends.
            
            ## Strategic Recommendations
            Concrete next steps for our product strategy based on these insights.
            
            Requirements:
            - Structure by competitor first, then their changes
            - Include specific numbers, features, and concrete changes
            - Provide actionable insights for each competitor
            - Focus on strategic implications and business impact
            - Use bullet points for readability
            """
            
            result = self.tools.llm.chat(
                question=summary_prompt,
                system_prompt="You are a senior product strategist creating competitive intelligence reports. Provide strategic insights and actionable recommendations for product teams."
            )
            
            state["weekly_summary"] = result["reply"]
            state["stage"] = "summary_generated"
            
            # Store report in database
            report_obj = Report(
                week=current_week,
                competitor_ids=list(competitor_summaries.keys()),
                summary=result["reply"],
                delivered_to=[]  # Will be updated after delivery
            )
            self.tools.db.add_report(report_obj)
            
            print("✅ Generated weekly summary report")
            return state
            
        except Exception as e:
            state["errors"].append(f"Summary generation failed: {str(e)}")
            state["stage"] = "error"
            return state

    async def deliver_report(self, state: AgentState) -> AgentState:
        """Deliver the report via Slack"""
        try:
            summary = state["weekly_summary"]
            current_week = datetime.now().strftime("%Y-W%U")
            
            # Create Slack message with blocks for better formatting
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📊 Weekly Competitor Report - {current_week}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Monitoring Summary*\n• {len(state['competitors'])} competitors tracked\n• {len(state['detected_changes'])} changes detected\n• {len(state['analysis_results'])} insights generated"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": summary[:2800]  # Slack has message limits
                    }
                }
            ]
            
            # Send to Slack
            result = self.tools.slack.send_block_message(blocks)
            
            state["delivery_status"] = result
            state["stage"] = "report_delivered"
            
            if result.get("ok"):
                print("✅ Report delivered successfully to Slack")
            else:
                print(f"❌ Failed to deliver report: {result.get('error')}")
                
            return state
            
        except Exception as e:
            state["errors"].append(f"Report delivery failed: {str(e)}")
            state["stage"] = "error"
            return state

    async def handle_errors(self, state: AgentState) -> AgentState:
        """Handle errors and cleanup"""
        if state["errors"]:
            print(f"❌ Errors encountered: {state['errors']}")
            
            # Send error notification
            error_message = f"Competitor tracking encountered errors:\n" + "\n".join(state["errors"])
            self.tools.slack.send_message(f"⚠️ Error Report: {error_message}")
        
        return state

    async def run_weekly_tracking(self) -> Dict[str, Any]:
        """Run the complete weekly tracking workflow"""
        print("🚀 Starting weekly competitor tracking...")
        
        # Initialize state
        initial_state: AgentState = {
            "stage": "starting",
            "competitors": [],
            "current_competitor": None,
            "website_snapshots": [],
            "app_updates": [],
            "social_posts": [],
            "detected_changes": [],
            "analysis_results": [],
            "weekly_summary": None,
            "delivery_status": {},
            "errors": [],
            "retry_count": 0
        }
        
        # Run the graph
        config = {"configurable": {"thread_id": f"weekly_tracking_{datetime.now().strftime('%Y%m%d')}"}}
        
        try:
            # Execute the workflow
            final_state = await self.graph.ainvoke(initial_state, config)
            
            return {
                "success": True,
                "stage": final_state.get("stage"),
                "competitors_tracked": len(final_state.get("competitors", [])),
                "changes_detected": len(final_state.get("detected_changes", [])),
                "summary_generated": bool(final_state.get("weekly_summary")),
                "delivered": final_state.get("delivery_status", {}).get("ok", False),
                "errors": final_state.get("errors", [])
            }
            
        except Exception as e:
            print(f"❌ Workflow execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# ================================
# SCHEDULER & MAIN EXECUTION
# ================================
class WeeklyScheduler:
    def __init__(self):
        self.agent = CompetitorTrackingAgent()
    
    async def run_scheduled_tracking(self):
        """Run weekly tracking (typically called via cron job)"""
        result = await self.agent.run_weekly_tracking()
        print("📋 Weekly tracking completed:")
        print(json.dumps(result, indent=2, default=str))
        return result
    
    async def run_on_demand_tracking(self, competitor_id: Optional[str] = None):
        """Run tracking on demand for specific competitor or all"""
        # Could add logic here to filter by specific competitor
        result = await self.agent.run_weekly_tracking()
        print("📋 On-demand tracking completed:")
        print(json.dumps(result, indent=2, default=str))
        return result

# ================================
# CLI INTERFACE
# ================================
async def main():
    """Main CLI interface"""
    import sys
    
    scheduler = WeeklyScheduler()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "weekly":
            await scheduler.run_scheduled_tracking()
        elif command == "ondemand":
            await scheduler.run_on_demand_tracking()
        elif command == "test":
            # Test run with minimal data
            print("🧪 Running test tracking...")
            await scheduler.run_on_demand_tracking()
        else:
            print("Usage: python competitor_tracker.py [weekly|ondemand|test]")
    else:
        # Default to weekly run
        await scheduler.run_scheduled_tracking()

if __name__ == "__main__":
    asyncio.run(main())