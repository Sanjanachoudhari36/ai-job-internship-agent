import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import engine, Base, SessionLocal, IS_MONGODB, get_db
from app.seed_data import seed_database
from app.routers import (
    auth_routes,
    profile_routes,
    job_routes,
    match_routes,
    agent_routes,
    application_routes,
    interview_routes,
    analytics_routes,
    workflow_routes
)

# Initialize database schema if SQL
if not IS_MONGODB and engine:
    Base.metadata.create_all(bind=engine)

# Seed initial jobs and demo candidate if empty
db_gen = get_db()
db = next(db_gen)
try:
    seed_database(db)
finally:
    try:
        db_gen.close()
    except Exception:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic AI-powered career automation platform for job discovery, multi-factor compatibility scoring, resume ATS optimization, personalized cover letters, Kanban tracking, and AI mock interview preparation.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local development and API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_routes.router, prefix=settings.API_PREFIX)
app.include_router(profile_routes.router, prefix=settings.API_PREFIX)
app.include_router(job_routes.router, prefix=settings.API_PREFIX)
app.include_router(match_routes.router, prefix=settings.API_PREFIX)
app.include_router(agent_routes.router, prefix=settings.API_PREFIX)
app.include_router(application_routes.router, prefix=settings.API_PREFIX)
app.include_router(interview_routes.router, prefix=settings.API_PREFIX)
app.include_router(analytics_routes.router, prefix=settings.API_PREFIX)
app.include_router(workflow_routes.router, prefix=settings.API_PREFIX)

# Static Files Directory
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(STATIC_DIR / "css", exist_ok=True)
os.makedirs(STATIC_DIR / "js", exist_ok=True)
os.makedirs(STATIC_DIR / "js" / "components", exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database_type": "MongoDB Atlas" if IS_MONGODB else "SQL",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# SPA Fallback: Serve index.html for all non-API routes
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": f"{settings.PROJECT_NAME} Backend API is running. Access /docs for Swagger UI."}
