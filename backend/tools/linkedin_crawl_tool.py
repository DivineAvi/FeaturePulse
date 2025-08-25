# linkedin_crawl_tool.py
from typing import Dict, List
from utils.crawler import CRAWLER
import re

class LinkedInCrawlTool:
    @property
    def definition(self) -> Dict:
        return {
            "type": "function",
            "name": "crawl_linkedin_posts",
            "description": "Crawl LinkedIn profile or company page to extract recent posts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "linkedin_url": {
                        "type": "string",
                        "description": "Public LinkedIn profile or company page URL"
                    },
                    "max_posts": {
                        "type": "integer",
                        "description": "Maximum number of posts to return",
                        "default": 5
                    }
                },
                "required": ["linkedin_url"]
            }
        }

    async def run(self, linkedin_url: str, max_posts: int = 5) -> Dict:
        try:
            # Crawl the LinkedIn page
            results = await CRAWLER.crawl_pages([linkedin_url], scroll=True)
            html_content = results.get(linkedin_url, "")

            # Extract posts (simplified example, may need adjustment for real LinkedIn)
            posts = re.findall(r'<div class=".*?post-content.*?">(.*?)</div>', html_content, re.DOTALL)
            posts = [re.sub(r"<.*?>", "", p).strip() for p in posts]  # remove HTML tags
            posts = posts[:max_posts]

            return {
                "linkedin_url": linkedin_url,
                "posts": posts
            }
        except Exception as e:
            return {"error": str(e)}
