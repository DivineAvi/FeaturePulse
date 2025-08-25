from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import uvicorn
from routes.router import router
from config import CONFIG
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{CONFIG.FRONTEND_URL}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return logo
    
app.include_router(router=router)
    
if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=8000)
