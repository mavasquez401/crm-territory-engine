"""
Client API Routes

Endpoints for client data and hierarchy queries.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging

from crm_mock_api.models import Client, ClientDetail, ClientHierarchyNode
from crm_mock_api.database import db

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("/", response_model=List[ClientDetail])
async def list_clients(
    region: str = Query(None, description="Filter by region"),
    segment: str = Query(None, description="Filter by segment"),
    search: str = Query(None, description="Search by client name"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List all clients with optional filtering and pagination.
    
    Supports filtering by region, segment, and text search.
    """
    logger.info(f"Listing clients (region={region}, segment={segment}, search={search})")
    
    # Get clients and assignments
    clients = db.get_clients()
    assignments = db.get_assignments()
    
    # Apply filters
    if region:
        clients = clients[clients['region'] == region]
    if segment:
        clients = clients[clients['segment'] == segment]
    if search:
        # Case-insensitive search in client name
        clients = clients[
            clients['client_name'].str.contains(search, case=False, na=False)
        ]
    
    # Apply pagination
    total = len(clients)
    clients = clients.iloc[offset:offset + limit]
    
    # Merge with assignments
    result = []
    for _, client in clients.iterrows():
        # Get assignment for this client
        assignment = assignments[assignments['client_key'] == client['client_key']]
        
        territory_id = None
        assignment_type = None
        if not assignment.empty:
            territory_id = assignment.iloc[0]['territory_id']
            assignment_type = assignment.iloc[0].get('assignment_type', 'PRIMARY')
        
        result.append(ClientDetail(
            client_key=int(client['client_key']),
            client_name=client['client_name'],
            region=client['region'],
            segment=client['segment'],
            parent_org=client['parent_org'],
            primary_advisor_email=client['primary_advisor_email'],
            is_active=bool(client.get('is_active', True)),
            territory_id=territory_id,
            assignment_type=assignment_type
        ))
    
    logger.info(f"Returning {len(result)} clients (total: {total})")
    return result


@router.get("/{client_id}", response_model=ClientDetail)
async def get_client(client_id: int):
    """
    Get detailed information about a specific client.
    """
    logger.info(f"Getting client: {client_id}")
    
    # Get client
    client = db.get_client_by_id(client_id)
    
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    
    # Get assignment
    assignments = db.get_assignments()
    assignment = assignments[assignments['client_key'] == client_id]
    
    territory_id = None
    assignment_type = None
    if not assignment.empty:
        territory_id = assignment.iloc[0]['territory_id']
        assignment_type = assignment.iloc[0].get('assignment_type', 'PRIMARY')
    
    return ClientDetail(
        client_key=int(client['client_key']),
        client_name=client['client_name'],
        region=client['region'],
        segment=client['segment'],
        parent_org=client['parent_org'],
        primary_advisor_email=client['primary_advisor_email'],
        is_active=bool(client.get('is_active', True)),
        territory_id=territory_id,
        assignment_type=assignment_type
    )


@router.get("/hierarchy", response_model=List[ClientHierarchyNode])
async def get_client_hierarchy():
    """
    Get client organizational hierarchy grouped by parent organization.
    
    Returns a tree structure of organizations and their clients.
    """
    logger.info("Getting client hierarchy")
    
    # Get hierarchy from database
    hierarchy = db.get_client_hierarchy()
    
    # Convert to response model
    result = []
    for org in hierarchy:
        # Convert client dicts to Client models
        clients = [
            Client(
                client_key=int(c['client_key']),
                client_name=c['client_name'],
                region=c['region'],
                segment=c['segment'],
                parent_org=c['parent_org'],
                primary_advisor_email=c['primary_advisor_email'],
                is_active=bool(c.get('is_active', True))
            )
            for c in org['clients']
        ]
        
        result.append(ClientHierarchyNode(
            parent_org=org['parent_org'],
            clients=clients,
            client_count=org['client_count']
        ))
    
    return result
