from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import uvicorn
from routes.router import router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
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
