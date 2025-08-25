import asyncio
from ctypes import Array
from typing import List, Set
from playwright.async_api import async_playwright,Page,ElementHandle
from urllib.parse import urljoin, urlparse, urldefrag
import re

from utils.utils import clean_and_hash, clean_html

#############################################################
##                      SCRAPPER CLASS
##          Can Have Multiple pages to scrap data
##
#############################################################

class Crawler:

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.pages: list[Page] = []
        self.context = None

    ##############################################
    #           SETUP BROWSER CONTEXT
    ##############################################
    async def init(self):
        """Launch browser and create a context"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()

    ##############################################
    # Create new page and appends to page list
    ##############################################
    async def new_page(self) -> Page:
        """Open a new page (tab)"""
        if not self.context:
            raise RuntimeError("Browser not initialized. Call init().")
        page = await self.context.new_page()
        self.pages.append(page)
        return page

    ##############################################
    # Go to url on a page
    ##############################################
    async def goto(self, page: Page, url: str):
        """Navigate a specific page to a URL"""
        await page.goto(url, wait_until="domcontentloaded")

    ##############################################
    # Create new page and appends to page list
    ##############################################
    async def get_text(self, page: Page, selector: str) -> str | None:
        """Get text from a selector on a specific page"""
        el = await page.query_selector(selector)
        return await el.text_content() if el else None

    ##############################################
    # Get all text
    ##############################################
    async def get_all_texts(self, page: Page, selector: str) -> list[str]:
        """Get multiple texts from a page"""
        els = await page.query_selector_all(selector)
        return [await el.text_content() for el in els]

    ##############################################
    # Get all elements from a list of selectors
    ##############################################
    async def get_all_elements(self, page: Page, selectors: List[str]) -> List[ElementHandle]:
        all_elements: List[ElementHandle] = []
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            all_elements.extend(elements)  
        return all_elements

    ##############################################
    # Scroll page until no more new content
    ##############################################
    async def infinite_scroll(
        self, 
        page: Page, 
        scroll_pause: float = 1.0, 
        max_scrolls: int = 50
    ):
        """
        Scrolls down the page repeatedly to load dynamic content.
        - scroll_pause: seconds to wait after each scroll
        - max_scrolls: stop after this many scrolls
        """
        last_height = await page.evaluate("() => document.body.scrollHeight")
        for _ in range(max_scrolls):
            await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(scroll_pause)

            new_height = await page.evaluate("() => document.body.scrollHeight")
            if new_height == last_height:
                # No new content loaded
                break
            last_height = new_height

    ##############################################
    # Normalize URL to handle fragments and duplicates
    ##############################################
    def normalize_url(self, url: str, base_url: str) -> str:
        """
        Normalize URL by:
        1. Converting relative URLs to absolute
        2. Removing fragments (# parts)
        3. Normalizing the URL structure
        """
        # Convert relative URL to absolute
        absolute_url = urljoin(base_url, url)
        
        # Remove fragment (everything after #)
        normalized_url, _ = urldefrag(absolute_url)
        
        # Remove trailing slash for consistency
        if normalized_url.endswith('/') and normalized_url != base_url.rstrip('/') + '/':
            normalized_url = normalized_url.rstrip('/')
            
        return normalized_url

    ##############################################
    # Check if URL should be crawled
    ##############################################
    def should_crawl_url(self, url: str, base_domain: str) -> bool:
        """
        Determine if URL should be crawled based on various criteria
        """
        try:
            parsed = urlparse(url)
            
            # Skip if no scheme or invalid URL
            if not parsed.scheme or parsed.scheme not in ['http', 'https']:
                return False
                
            # Skip if different domain (optional - remove if you want to crawl external links)
            if parsed.netloc and parsed.netloc != base_domain:
                return False
                
            # Skip common file extensions that aren't web pages
            skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.doc', '.docx', '.mp4', '.mp3'}
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
                
            # Skip mailto, tel, and other non-http schemes
            if parsed.scheme in ['mailto', 'tel', 'javascript']:
                return False
                
            return True
            
        except Exception:
            return False

    ###################################
    ## MAIN CRAWL WEBSITE FUNCTION
    ###################################
    async def crawl_website(
        self, 
        url: str, 
        scroll: bool = False,
        smart_scroll: bool = False, 
        max_pages: int = 50,
        visited_urls: Set[str] = None
    ) -> dict[str, str]:
        """
        Crawl website recursively following links
        
        Args:
            url: Starting URL
            scroll: Whether to scroll pages to load dynamic content
            smart_scroll: Whether to use intelligent scrolling
            max_pages: Maximum number of pages to crawl
            visited_urls: Set of already visited URLs
            
        Returns:
            Dictionary mapping URLs to their cleaned content
        """
        if visited_urls is None:
            visited_urls = set()
            
        results = {}
        urls_to_visit = [url]
        base_domain = urlparse(url).netloc
        
        # Initialize browser if not already done
        if not self.browser:
            await self.init()
        
        while urls_to_visit and len(results) < max_pages:
            current_url = urls_to_visit.pop(0)
            normalized_url = self.normalize_url(current_url, url)
            
            # Skip if already visited
            if normalized_url in visited_urls:
                continue
                
            try:
                print(f"Crawling: {normalized_url}")
                visited_urls.add(normalized_url)
                
                # Create new page for this URL
                page = await self.new_page()
                await self.goto(page, normalized_url)
                
                # Handle scrolling if requested
                if scroll or smart_scroll:
                    if smart_scroll:
                        # Smart scrolling - detect if page has infinite scroll
                        initial_height = await page.evaluate("() => document.body.scrollHeight")
                        await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(1)
                        new_height = await page.evaluate("() => document.body.scrollHeight")
                        
                        if new_height > initial_height:
                            # Page has dynamic content, do infinite scroll
                            await self.infinite_scroll(page, scroll_pause=1.0, max_scrolls=10)
                    else:
                        await self.infinite_scroll(page)
                
                # Get page content
                html = await page.content()
                cleaned_text, content_hash = clean_and_hash(html)
                # Store cleaned text; hash is used by callers when needed
                results[normalized_url] = cleaned_text
                
                # Extract all links from current page
                link_elements = await page.query_selector_all('a[href]')
                
                for link_element in link_elements:
                    try:
                        href = await link_element.get_attribute('href')
                        if href:
                            # Normalize the link URL
                            link_url = self.normalize_url(href, normalized_url)
                            
                            # Check if we should crawl this URL
                            if (self.should_crawl_url(link_url, base_domain) and 
                                link_url not in visited_urls and 
                                link_url not in urls_to_visit):
                                urls_to_visit.append(link_url)
                                
                    except Exception as e:
                        print(f"Error processing link: {e}")
                        continue
                
                # Close the page to free memory
                await page.close()
                
            except Exception as e:
                print(f"Error crawling {normalized_url}: {e}")
                continue
        
        return results

    ###################################
    ## EXISTING CRAWL PAGES FUNCTION
    ##################################
    async def crawl_pages(self, urls: list[str], scroll: bool = False) -> dict[str, str]:
        """
        Crawl multiple URLs and return cleaned HTML text.
        Returns: {url: cleaned_text}
        """
        results = {}
        await self.init()

        for url in urls:
            page = await self.new_page()
            await self.goto(page, url)

            if scroll:
                await self.infinite_scroll(page)

            html = await page.content()
            results[url] = clean_html(html)

        await self.close()
        return results

    ##############################################
    # Closes browser session
    ##############################################
    async def close(self):
        """Close everything"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

CRAWLER = Crawler(headless=False)

# Example usage:
async def main():
    crawler = Crawler()
    try:
        results = await crawler.crawl_website(
            "https://example.com", 
            scroll=False, 
            smart_scroll=True,
            max_pages=10
        )
        
        print(f"Crawled {len(results)} pages:")
        for url in results.keys():
            print(f"- {url}")
            
    finally:
        await crawler.close()

# Run with: asyncio.run(main())