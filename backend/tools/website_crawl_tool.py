from typing import Dict
from utils.crawler import CRAWLER

class WebsiteCrawlTool:
    @property
    def definition(self) -> Dict:
        return {
            "type": "function",
            "name": "crawl_website",
            "description": "Crawl a website and return cleaned text from its pages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Starting URL of the website to crawl"
                    },
                    "max_pages": {
                        "type": "integer",
                        "description": "Maximum number of pages to crawl",
                        "default": 10
                    },
                    "scroll": {
                        "type": "boolean",
                        "description": "Whether to use infinite scroll",
                        "default": False
                    },
                    "smart_scroll": {
                        "type": "boolean",
                        "description": "Whether to detect and apply smart scrolling",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        }

    async def run(
        self, 
        url: str, 
        max_pages: int = 10, 
        scroll: bool = False, 
        smart_scroll: bool = True
    ) -> Dict[str, str]:
        """
        Run the crawler on the given website.
        Returns {url: cleaned_text}
        """
        try:
            results = await CRAWLER.crawl_website(
                url=url,
                max_pages=max_pages,
                scroll=scroll,
                smart_scroll=smart_scroll
            )
            return results
        except Exception as e:
            return {"error": str(e)}
