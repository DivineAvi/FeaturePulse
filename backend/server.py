from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
from routes.router import router
from utils.crawler import CRAWLER
app = FastAPI()

logo = """
███████╗ ███████╗ ██████╗  ██╗   ██╗ ███████╗ ██████╗ 
██╔════╝ ██╔════╝ ██╔══██╗ ██║   ██║ ██╔════╝ ██╔══██╗
███████╗ █████╗   ██████╔╝ ██║   ██║ █████╗   ██████╔╝
╚════██║ ██╔══╝   ██╔══██╗ ╚██╗ ██╔╝ ██╔══╝   ██╔══██╗
███████║ ███████╗ ██║  ██║  ╚████╔╝  ███████╗ ██║  ██║  is running .
╚══════╝ ╚══════╝ ╚═╝  ╚═╝   ╚═══╝   ╚══════╝ ╚═╝  ╚═╝
"""

@app.get("/", response_class=PlainTextResponse)
async def show_logo():
    await CRAWLER.init()
    print(await CRAWLER.crawl_website("https://cursor.com/",True,max_pages=1))
    return logo
    
app.include_router(router=router)
    
if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=8000)
