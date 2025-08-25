import requests
from typing import Dict

class AppStoreTool:
    @property
    def definition(self) -> Dict:
        return {
            "type": "function",
            "name": "appstore_app_info",
            "description": "Fetch metadata about an app from the Apple App Store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_id": {
                        "type": "string",
                        "description": "The App Store app ID (e.g., 284882215 for Facebook)."
                    },
                    "country": {
                        "type": "string",
                        "description": "Country code for store (default: 'us')"
                    }
                },
                "required": ["app_id"]
            }
        }

    async def run(self, app_id: str, country: str = "us") -> Dict:
        """Fetch Apple App Store app info"""
        try:
            url = f"https://itunes.apple.com/lookup?id={app_id}&country={country}"
            resp = requests.get(url)
            data = resp.json()

            if not data.get("results"):
                return {"error": "App not found"}

            app_data = data["results"][0]
            return {
                "title": app_data.get("trackName"),
                "developer": app_data.get("sellerName"),
                "version": app_data.get("version"),
                "updated": app_data.get("currentVersionReleaseDate"),
                "score": app_data.get("averageUserRating"),
                "ratings": app_data.get("userRatingCount"),
                "description": app_data.get("description"),
                "release_notes": app_data.get("releaseNotes"),
                "icon": app_data.get("artworkUrl100"),
                "url": app_data.get("trackViewUrl")
            }
        except Exception as e:
            return {"error": str(e)}
