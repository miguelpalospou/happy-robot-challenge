from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os

from config import get_settings, Settings
from database import init_supabase, get_supabase
from routers import loads, carriers, negotiations, calls, metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str = Security(api_key_header),
    settings: Settings = Depends(get_settings)
):
    if not api_key or api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    init_supabase(settings.supabase_url, settings.supabase_service_key)
    logger.info("Supabase client initialized")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Happy Robot - Inbound Carrier Sales API",
    description="API for automating inbound carrier calls for freight load sales",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loads.router, prefix="/loads", tags=["Loads"], dependencies=[Depends(verify_api_key)])
app.include_router(carriers.router, prefix="/carriers", tags=["Carriers"], dependencies=[Depends(verify_api_key)])
app.include_router(negotiations.router, prefix="/negotiations", tags=["Negotiations"], dependencies=[Depends(verify_api_key)])
app.include_router(calls.router, prefix="/calls", tags=["Calls"], dependencies=[Depends(verify_api_key)])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"], dependencies=[Depends(verify_api_key)])


# Mount static files for dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "happy-robot-carrier-sales"}


@app.get("/")
async def root():
    """Serve landing page"""
    landing = os.path.join(os.path.dirname(__file__), "static", "landing.html")
    if os.path.exists(landing):
        return FileResponse(landing)
    return {"message": "Happy Robot - Inbound Carrier Sales API", "docs": "/docs"}


@app.get("/dashboard")
async def dashboard():
    """Serve analytics dashboard"""
    static_index = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    raise HTTPException(status_code=404, detail="Dashboard not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
