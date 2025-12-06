"""
Advisor API Routes

Endpoints for advisor workload and statistics.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging

from crm_mock_api.models import Advisor, AdvisorDetail, AdvisorStats, Client
from crm_mock_api.database import db

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/advisors", tags=["advisors"])


@router.get("/", response_model=List[Advisor])
async def list_advisors(
    region: str = Query(None, description="Filter by region")
):
    """
    List all advisors with workload metrics.
    
    Optionally filter by region.
    """
    logger.info(f"Listing advisors (region={region})")
    
    # Get assignments
    assignments = db.get_assignments()
    
    # Filter by region if requested
    if region:
        territories = db.get_territories()
        region_territories = territories[territories['region'] == region]['territory_id'].tolist()
        assignments = assignments[assignments['territory_id'].isin(region_territories)]
    
    # Group by advisor
    result = []
    for advisor_email in assignments['primary_advisor_email'].unique():
        advisor_assignments = assignments[
            assignments['primary_advisor_email'] == advisor_email
        ]
        
        # Get unique territories and regions
        territories = db.get_territories()
        advisor_territories = advisor_assignments['territory_id'].unique()
        advisor_territory_data = territories[
            territories['territory_id'].isin(advisor_territories)
        ]
        
        regions = advisor_territory_data['region'].unique().tolist()
        
        result.append(Advisor(
            advisor_email=advisor_email,
            client_count=int(advisor_assignments['client_key'].nunique()),
            territory_count=len(advisor_territories),
            regions=regions
        ))
    
    # Sort by client count descending
    result.sort(key=lambda x: x.client_count, reverse=True)
    
    return result


@router.get("/{advisor_email}/workload", response_model=AdvisorDetail)
async def get_advisor_workload(advisor_email: str):
    """
    Get detailed workload information for a specific advisor.
    
    Includes list of clients and territories.
    """
    logger.info(f"Getting workload for advisor: {advisor_email}")
    
    # Get assignments for this advisor
    assignments = db.get_assignments_by_advisor(advisor_email)
    
    if assignments.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Advisor {advisor_email} not found or has no assignments"
        )
    
    # Get client details
    clients = db.get_clients()
    advisor_clients = []
    
    for client_key in assignments['client_key'].unique():
        client = clients[clients['client_key'] == client_key]
        if not client.empty:
            client_data = client.iloc[0]
            advisor_clients.append(Client(
                client_key=int(client_data['client_key']),
                client_name=client_data['client_name'],
                region=client_data['region'],
                segment=client_data['segment'],
                parent_org=client_data['parent_org'],
                primary_advisor_email=client_data['primary_advisor_email'],
                is_active=bool(client_data.get('is_active', True))
            ))
    
    # Get territories
    territories = assignments['territory_id'].unique().tolist()
    
    # Get regions
    territories_df = db.get_territories()
    advisor_territory_data = territories_df[
        territories_df['territory_id'].isin(territories)
    ]
    regions = advisor_territory_data['region'].unique().tolist()
    
    return AdvisorDetail(
        advisor_email=advisor_email,
        client_count=len(advisor_clients),
        territory_count=len(territories),
        regions=regions,
        clients=advisor_clients,
        territories=territories
    )


@router.get("/stats", response_model=AdvisorStats)
async def get_advisor_stats():
    """
    Get overall advisor statistics.
    
    Returns aggregated metrics across all advisors.
    """
    logger.info("Getting advisor statistics")
    
    # Get all advisors
    advisors = await list_advisors()
    
    if not advisors:
        return AdvisorStats(
            total_advisors=0,
            avg_clients_per_advisor=0.0,
            max_clients=0,
            min_clients=0
        )
    
    # Calculate statistics
    client_counts = [a.client_count for a in advisors]
    
    return AdvisorStats(
        total_advisors=len(advisors),
        avg_clients_per_advisor=sum(client_counts) / len(client_counts),
        max_clients=max(client_counts),
        min_clients=min(client_counts)
    )
