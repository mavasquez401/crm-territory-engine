"""
Territory API Routes

Endpoints for territory management and queries.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging

from crm_mock_api.models import Territory, TerritoryDetail, Assignment
from crm_mock_api.database import db

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/territories", tags=["territories"])


@router.get("/", response_model=List[Territory])
async def list_territories(
    region: str = Query(None, description="Filter by region"),
    segment: str = Query(None, description="Filter by segment")
):
    """
    List all territories with client and advisor counts.
    
    Optionally filter by region or segment.
    """
    logger.info(f"Listing territories (region={region}, segment={segment})")
    
    # Get territories and assignments
    territories = db.get_territories()
    assignments = db.get_assignments()
    
    # Filter if requested
    if region:
        territories = territories[territories['region'] == region]
    if segment:
        territories = territories[territories['segment'] == segment]
    
    # Add counts
    result = []
    for _, territory in territories.iterrows():
        territory_id = territory['territory_id']
        
        # Get assignments for this territory
        territory_assignments = assignments[
            assignments['territory_id'] == territory_id
        ]
        
        # Count unique clients and advisors
        client_count = territory_assignments['client_key'].nunique()
        advisor_count = territory_assignments['primary_advisor_email'].nunique()
        
        result.append(Territory(
            territory_id=territory_id,
            region=territory['region'],
            segment=territory['segment'],
            owner_role=territory.get('owner_role', 'Sales Rep'),
            client_count=client_count,
            advisor_count=advisor_count,
            is_active=True
        ))
    
    return result


@router.get("/{territory_id}", response_model=TerritoryDetail)
async def get_territory(territory_id: str):
    """
    Get detailed information about a specific territory.
    """
    logger.info(f"Getting territory: {territory_id}")
    
    # Get territory
    territory = db.get_territory_by_id(territory_id)
    
    if not territory:
        raise HTTPException(status_code=404, detail=f"Territory {territory_id} not found")
    
    # Get assignments for counts
    assignments = db.get_assignments_by_territory(territory_id)
    client_count = assignments['client_key'].nunique()
    advisor_count = assignments['primary_advisor_email'].nunique()
    
    return TerritoryDetail(
        territory_id=territory['territory_id'],
        region=territory['region'],
        segment=territory['segment'],
        owner_role=territory.get('owner_role', 'Sales Rep'),
        client_count=client_count,
        advisor_count=advisor_count,
        is_active=True,
        description=f"{territory['region']} - {territory['segment']}"
    )


@router.get("/{territory_id}/assignments", response_model=List[Assignment])
async def get_territory_assignments(territory_id: str):
    """
    Get all client assignments for a specific territory.
    """
    logger.info(f"Getting assignments for territory: {territory_id}")
    
    # Verify territory exists
    territory = db.get_territory_by_id(territory_id)
    if not territory:
        raise HTTPException(status_code=404, detail=f"Territory {territory_id} not found")
    
    # Get assignments
    assignments = db.get_assignments_by_territory(territory_id)
    
    # Get client names
    clients = db.get_clients()
    
    # Merge to get client names
    result = []
    for _, assignment in assignments.iterrows():
        client = clients[clients['client_key'] == assignment['client_key']]
        if not client.empty:
            client_name = client.iloc[0]['client_name']
        else:
            client_name = "Unknown"
        
        result.append(Assignment(
            client_key=int(assignment['client_key']),
            client_name=client_name,
            territory_id=assignment['territory_id'],
            primary_advisor_email=assignment['primary_advisor_email'],
            assignment_type=assignment.get('assignment_type', 'PRIMARY'),
            is_current=bool(assignment.get('is_current', True))
        ))
    
    return result
