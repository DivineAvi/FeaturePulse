# scraper.py
import asyncio
from typing import List
from playwright.async_api import async_playwright,Page,ElementHandle

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
    # Closes browser session
    ##############################################
    async def close(self):
        """Close everything"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

CRAWLER = Crawler()