#!/usr/bin/env python3
"""
Test script for Play Store Tool
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.playstore_tool import PlayStoreTool

async def test_playstore_tool():
    """Test the Play Store tool with popular apps"""
    
    playstore_tool = PlayStoreTool()
    
    # Test apps (popular apps with known package names)
    test_apps = [
        "com.whatsapp",  # WhatsApp
        "com.instagram.android",  # Instagram
        "com.google.android.youtube",  # YouTube
        "com.spotify.music",  # Spotify
        "com.discord",  # Discord
    ]
    
    print("🧪 Testing Play Store Tool...")
    print("=" * 50)
    
    for package_name in test_apps:
        print(f"\n📱 Testing: {package_name}")
        try:
            result = await playstore_tool.run(package_name)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success!")
                print(f"   Title: {result.get('title', 'N/A')}")
                print(f"   Developer: {result.get('developer', 'N/A')}")
                print(f"   Version: {result.get('version', 'N/A')}")
                print(f"   Updated: {result.get('updated', 'N/A')}")
                print(f"   Score: {result.get('score', 'N/A')}")
                print(f"   Installs: {result.get('installs', 'N/A')}")
                print(f"   URL: {result.get('url', 'N/A')}")
                
                if result.get('release_notes'):
                    print(f"   Recent Changes: {result['release_notes'][:100]}...")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Play Store Tool Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_playstore_tool())
