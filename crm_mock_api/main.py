"""
FastAPI Main Application

Mock CRM API for territory and client management.
Provides REST endpoints for the React dashboard.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from crm_mock_api.routers import territories, clients, advisors, assignments, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="CRM Territory Management API",
    description="REST API for Enterprise CRM Territory & Segmentation Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:80",    # Docker frontend
        "http://localhost",       # Docker frontend (no port)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(territories.router)
app.include_router(clients.router)
app.include_router(advisors.router)
app.include_router(assignments.router)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Logs API startup and configuration.
    """
    logger.info("=" * 50)
    logger.info("CRM Territory Management API Starting")
    logger.info("=" * 50)
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("ReDoc Documentation: http://localhost:8000/redoc")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    """
    logger.info("CRM Territory Management API Shutting Down")


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "CRM Territory Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": {
            "territories": "/api/territories",
            "clients": "/api/clients",
            "advisors": "/api/advisors",
            "assignments": "/api/assignments",
            "stats": "/api/stats"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
