"""
Dimensional Model Transformation Module

Transforms raw client data into star schema dimensional model:
- CLIENT_DIM: Client master data
- TERRITORY_DIM: Territory definitions
- ASSIGNMENTS_FACT: Client-territory assignments
"""

import pandas as pd
import logging
from typing import Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_client_dim(clients_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build CLIENT_DIM dimension table from raw client data.
    
    Args:
        clients_df: Raw client data DataFrame
        
    Returns:
        CLIENT_DIM DataFrame with standardized columns
    """
    logger.info("Building CLIENT_DIM dimension table")
    
    # Rename columns to match dimensional model
    client_dim = clients_df.rename(
        columns={
            "client_id": "client_key",
            "client_name": "client_name",
            "region": "region",
            "segment": "segment",
            "parent_org": "parent_org",
            "advisor_email": "primary_advisor_email",
        }
    ).copy()
    
    # Add derived columns
    client_dim["is_active"] = True
    
    # Data validation
    if client_dim["client_key"].duplicated().any():
        logger.warning("Duplicate client_key values found in CLIENT_DIM")
    
    logger.info(f"Created CLIENT_DIM with {len(client_dim)} rows")
    return client_dim


def build_territory_dim(client_dim: pd.DataFrame) -> pd.DataFrame:
    """
    Build TERRITORY_DIM dimension table from client data.
    
    Territories are defined by unique combinations of region and segment.
    Territory IDs are generated as: {REGION_PREFIX}_{SEGMENT_PREFIX}
    
    Args:
        client_dim: CLIENT_DIM DataFrame
        
    Returns:
        TERRITORY_DIM DataFrame with territory definitions
    """
    logger.info("Building TERRITORY_DIM dimension table")
    
    # Extract unique region-segment combinations
    territory_dim = (
        client_dim[["region", "segment"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    
    # Generate territory IDs: First 3 letters of region + first 3 letters of segment
    territory_dim["territory_id"] = (
        territory_dim["region"].str[:3].str.upper()
        + "_"
        + territory_dim["segment"].str[:3].str.upper()
    )
    
    # Add owner role (default to Sales Rep)
    territory_dim["owner_role"] = "Sales Rep"
    
    logger.info(f"Created TERRITORY_DIM with {len(territory_dim)} territories")
    logger.info(f"Territories: {territory_dim['territory_id'].tolist()}")
    
    return territory_dim


def build_assignments_fact(
    client_dim: pd.DataFrame,
    territory_dim: pd.DataFrame
) -> pd.DataFrame:
    """
    Build ASSIGNMENTS_FACT table linking clients to territories.
    
    Joins clients with territories based on region and segment,
    creating the fact table for the star schema.
    
    Args:
        client_dim: CLIENT_DIM DataFrame
        territory_dim: TERRITORY_DIM DataFrame
        
    Returns:
        ASSIGNMENTS_FACT DataFrame with client-territory assignments
    """
    logger.info("Building ASSIGNMENTS_FACT table")
    
    # Join clients with territories on region and segment
    assignments_fact = client_dim.merge(
        territory_dim,
        on=["region", "segment"],
        how="left",
    )[["client_key", "territory_id", "primary_advisor_email"]]
    
    # Add assignment metadata
    assignments_fact["assignment_type"] = "PRIMARY"
    assignments_fact["is_current"] = True
    
    # Check for unassigned clients (null territory_id)
    unassigned = assignments_fact["territory_id"].isna().sum()
    if unassigned > 0:
        logger.warning(f"Found {unassigned} clients without territory assignment")
    
    logger.info(f"Created ASSIGNMENTS_FACT with {len(assignments_fact)} assignments")
    
    return assignments_fact


def transform_to_dimensional_model(
    raw_clients: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Main transformation function to convert raw data to dimensional model.
    
    Args:
        raw_clients: Raw client data DataFrame
        
    Returns:
        Tuple of (client_dim, territory_dim, assignments_fact)
    """
    logger.info("Starting dimensional model transformation")
    
    # Build dimension tables
    client_dim = build_client_dim(raw_clients)
    territory_dim = build_territory_dim(client_dim)
    
    # Build fact table
    assignments_fact = build_assignments_fact(client_dim, territory_dim)
    
    logger.info("Dimensional model transformation complete")
    
    return client_dim, territory_dim, assignments_fact


