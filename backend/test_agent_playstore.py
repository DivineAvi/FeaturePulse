#!/usr/bin/env python3
"""
Test script for Play Store Tool integration with Agent
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.feature_pulse_agent import CompetitorTrackingTools

async def test_agent_playstore_integration():
    """Test the Play Store tool integration with the agent"""
    
    print("🧪 Testing Play Store Tool Integration with Agent...")
    print("=" * 60)
    
    # Initialize the tools
    tools = CompetitorTrackingTools()
    
    # Test with a competitor that has Play Store URLs
    test_competitor = {
        "id": "test_competitor_1",
        "name": "Test App Company",
        "tracking_urls": [
            "https://play.google.com/store/apps/details?id=com.whatsapp",
            "https://play.google.com/store/apps/details?id=com.instagram.android",
            "https://play.google.com/store/apps/details?id=com.discord"
        ]
    }
    
    print(f"📱 Testing competitor: {test_competitor['name']}")
    print(f"🔗 Tracking URLs: {len(test_competitor['tracking_urls'])} Play Store URLs")
    
    app_updates = []
    
    for tracking_url in test_competitor.get("tracking_urls", []):
        url_str = str(tracking_url)
        
        if "play.google.com" in url_str:
            print(f"\n🔍 Processing: {url_str}")
            
            # Extract package name from Google Play Store URL
            package_name = url_str.split("/details?id=")[-1].split("&")[0] if "/details?id=" in url_str else None
            
            if package_name:
                print(f"📦 Package name: {package_name}")
                
                try:
                    result = await tools.get_app_info(package_name, "playstore")
                    
                    if result["success"] and not result["data"].get("error"):
                        app_update = {
                            "competitor_id": test_competitor["id"],
                            "store": "playstore",
                            "package_name": package_name,
                            "data": result["data"],
                            "timestamp": "2025-01-25T16:30:00Z"
                        }
                        app_updates.append(app_update)
                        
                        print(f"✅ Success! App: {result['data'].get('title', 'N/A')}")
                        print(f"   Developer: {result['data'].get('developer', 'N/A')}")
                        print(f"   Version: {result['data'].get('version', 'N/A')}")
                        print(f"   Score: {result['data'].get('score', 'N/A')}")
                        print(f"   Installs: {result['data'].get('installs', 'N/A')}")
                        
                        if result['data'].get('release_notes'):
                            print(f"   Recent Changes: {result['data']['release_notes'][:100]}...")
                    else:
                        print(f"❌ Failed to get app info: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ Exception: {str(e)}")
            else:
                print(f"❌ Could not extract package name from URL")
    
    print(f"\n📊 Summary:")
    print(f"   Total Play Store URLs processed: {len([url for url in test_competitor['tracking_urls'] if 'play.google.com' in str(url)])}")
    print(f"   Successful app updates: {len(app_updates)}")
    
    print("\n" + "=" * 60)
    print("🏁 Play Store Agent Integration Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_agent_playstore_integration())
