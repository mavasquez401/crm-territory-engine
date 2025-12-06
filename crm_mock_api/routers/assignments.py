"""
Assignment API Routes

Endpoints for assignment data and history.
"""

from fastapi import APIRouter, Query
from typing import List
import logging

from crm_mock_api.models import Assignment, AssignmentHistory
from crm_mock_api.database import db

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/assignments", tags=["assignments"])


@router.get("/", response_model=List[Assignment])
async def list_assignments(
    territory_id: str = Query(None, description="Filter by territory"),
    advisor_email: str = Query(None, description="Filter by advisor"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results")
):
    """
    List all current assignments.
    
    Optionally filter by territory or advisor.
    """
    logger.info(f"Listing assignments (territory={territory_id}, advisor={advisor_email})")
    
    # Get assignments
    assignments = db.get_assignments()
    
    # Apply filters
    if territory_id:
        assignments = assignments[assignments['territory_id'] == territory_id]
    if advisor_email:
        assignments = assignments[assignments['primary_advisor_email'] == advisor_email]
    
    # Limit results
    assignments = assignments.head(limit)
    
    # Get client names
    clients = db.get_clients()
    
    # Build response
    result = []
    for _, assignment in assignments.iterrows():
        client = clients[clients['client_key'] == assignment['client_key']]
        client_name = client.iloc[0]['client_name'] if not client.empty else "Unknown"
        
        result.append(Assignment(
            client_key=int(assignment['client_key']),
            client_name=client_name,
            territory_id=assignment['territory_id'],
            primary_advisor_email=assignment['primary_advisor_email'],
            assignment_type=assignment.get('assignment_type', 'PRIMARY'),
            is_current=bool(assignment.get('is_current', True))
        ))
    
    return result


@router.get("/history", response_model=List[AssignmentHistory])
async def get_assignment_history(
    client_id: int = Query(None, description="Filter by client ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results")
):
    """
    Get assignment change history.
    
    Shows historical changes to territory assignments.
    """
    logger.info(f"Getting assignment history (client_id={client_id})")
    
    # Get history from database
    history = db.get_assignment_history()
    
    if history.empty:
        logger.warning("No assignment history found")
        return []
    
    # Filter by client if requested
    if client_id:
        history = history[history['client_id'] == client_id]
    
    # Limit results
    history = history.head(limit)
    
    # Build response
    result = []
    for _, record in history.iterrows():
        result.append(AssignmentHistory(
            client_key=int(record.get('client_id', record.get('client_key', 0))),
            client_name=record.get('client_name', 'Unknown'),
            territory_id=record.get('new_territory', record.get('territory_id', '')),
            primary_advisor_email=record.get('primary_advisor_email', 'unknown@example.com'),
            assignment_type=record.get('assignment_type', 'PRIMARY'),
            is_current=bool(record.get('is_current', False)),
            assigned_by_rule=record.get('rule', record.get('assigned_by_rule'))
        ))
    
    return result
