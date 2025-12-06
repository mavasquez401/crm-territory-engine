"""
System API Routes

Health checks and system-wide statistics.
"""

from fastapi import APIRouter
from datetime import datetime

from models import HealthCheck, SystemStats
from database import db

# Create router
router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        API health status and version
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """
    Get overall system statistics.
    
    Returns:
        Aggregate statistics for the entire system
    """
    stats = db.get_system_stats()
    return stats


@router.post("/refresh")
async def refresh_data():
    """
    Refresh cached data from CSV files.
    
    Call this endpoint after running Airflow DAGs
    to reload the latest data.
    
    Returns:
        Success message
    """
    db.refresh_cache()
    return {
        "status": "success",
        "message": "Data cache refreshed",
        "timestamp": datetime.now().isoformat()
    }

