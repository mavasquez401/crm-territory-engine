"""
Health and System API Routes

Endpoints for health checks and system statistics.
"""

from fastapi import APIRouter
from datetime import datetime
import logging

from crm_mock_api.models import HealthCheck, SystemStats
from crm_mock_api.database import db

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint.
    
    Returns API status and version information.
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """
    Get overall system statistics.
    
    Returns counts and metrics for the entire system.
    """
    logger.info("Getting system statistics")
    
    # Get stats from database
    stats = db.get_system_stats()
    
    return SystemStats(
        total_clients=stats['total_clients'],
        total_territories=stats['total_territories'],
        total_advisors=stats['total_advisors'],
        total_assignments=stats['total_assignments'],
        avg_clients_per_territory=round(stats['avg_clients_per_territory'], 2),
        data_last_updated=stats['data_last_updated']
    )


