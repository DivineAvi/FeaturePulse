from google_play_scraper import app
from typing import Dict

class PlayStoreTool:
    @property
    def definition(self) -> Dict:
        return {
            "type": "function",
            "name": "playstore_app_info",
            "description": "Fetch metadata about an app from the Google Play Store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_name": {
                        "type": "string",
                        "description": "The package name of the app (e.g., com.facebook.katana)"
                    }
                },
                "required": ["package_name"]
            }
        }

    async def run(self, package_name: str) -> Dict:
        """Fetch Google Play Store app info"""
        try:
            data = app(package_name)
            return {
                "title": data.get("title"),
                "developer": data.get("developer"),
                "version": data.get("version"),
                "updated": data.get("updated"),
                "installs": data.get("installs"),
                "score": data.get("score"),
                "ratings": data.get("ratings"),
                "reviews": data.get("reviews"),
                "description": data.get("description"),
                "release_notes": data.get("recentChanges"),
                "icon": data.get("icon"),
                "url": data.get("url")
            }
        except Exception as e:
            return {"error": str(e)}
