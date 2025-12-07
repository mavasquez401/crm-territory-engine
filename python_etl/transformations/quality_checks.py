"""
Data Quality Checks Module

Validates data quality throughout the ETL pipeline:
- Row count validation
- Schema validation
- Referential integrity checks
- Data completeness checks
"""

import pandas as pd
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_row_counts(
    client_dim: pd.DataFrame,
    territory_dim: pd.DataFrame,
    assignments_fact: pd.DataFrame
) -> bool:
    """
    Validate that all tables have data (non-empty).
    
    Args:
        client_dim: CLIENT_DIM DataFrame
        territory_dim: TERRITORY_DIM DataFrame
        assignments_fact: ASSIGNMENTS_FACT DataFrame
        
    Returns:
        True if all validations pass
        
    Raises:
        AssertionError: If any table is empty
    """
    logger.info("Validating row counts")
    
    client_count = len(client_dim)
    territory_count = len(territory_dim)
    assignment_count = len(assignments_fact)
    
    logger.info(f"[QUALITY] client_dim rows: {client_count}")
    logger.info(f"[QUALITY] territory_dim rows: {territory_count}")
    logger.info(f"[QUALITY] assignments_fact rows: {assignment_count}")
    
    # Assert non-empty tables
    assert client_count > 0, "client_dim should not be empty"
    assert territory_count > 0, "territory_dim should not be empty"
    assert assignment_count > 0, "assignments_fact should not be empty"
    
    logger.info("[QUALITY] Row count checks passed")
    return True


def validate_schema(
    df: pd.DataFrame,
    required_columns: List[str],
    table_name: str
) -> bool:
    """
    Validate that DataFrame has all required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        table_name: Name of table (for logging)
        
    Returns:
        True if validation passes
        
    Raises:
        ValueError: If required columns are missing
    """
    logger.info(f"Validating schema for {table_name}")
    
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        raise ValueError(
            f"{table_name} missing required columns: {missing_columns}"
        )
    
    logger.info(f"[QUALITY] {table_name} schema validation passed")
    return True


def validate_referential_integrity(
    client_dim: pd.DataFrame,
    territory_dim: pd.DataFrame,
    assignments_fact: pd.DataFrame
) -> bool:
    """
    Validate referential integrity between tables.
    
    Checks:
    - All client_key in assignments exist in client_dim
    - All territory_id in assignments exist in territory_dim
    
    Args:
        client_dim: CLIENT_DIM DataFrame
        territory_dim: TERRITORY_DIM DataFrame
        assignments_fact: ASSIGNMENTS_FACT DataFrame
        
    Returns:
        True if all checks pass
        
    Raises:
        ValueError: If referential integrity violations found
    """
    logger.info("Validating referential integrity")
    
    # Check client_key foreign key
    valid_clients = set(client_dim["client_key"])
    assignment_clients = set(assignments_fact["client_key"])
    orphaned_clients = assignment_clients - valid_clients
    
    if orphaned_clients:
        raise ValueError(
            f"Found {len(orphaned_clients)} assignments with invalid client_key: "
            f"{list(orphaned_clients)[:5]}"
        )
    
    # Check territory_id foreign key
    valid_territories = set(territory_dim["territory_id"])
    assignment_territories = set(assignments_fact["territory_id"].dropna())
    orphaned_territories = assignment_territories - valid_territories
    
    if orphaned_territories:
        raise ValueError(
            f"Found {len(orphaned_territories)} assignments with invalid territory_id: "
            f"{list(orphaned_territories)[:5]}"
        )
    
    logger.info("[QUALITY] Referential integrity checks passed")
    return True


def validate_data_completeness(
    df: pd.DataFrame,
    required_non_null_columns: List[str],
    table_name: str
) -> bool:
    """
    Validate that required columns have no null values.
    
    Args:
        df: DataFrame to validate
        required_non_null_columns: Columns that must not have nulls
        table_name: Name of table (for logging)
        
    Returns:
        True if validation passes
        
    Raises:
        ValueError: If null values found in required columns
    """
    logger.info(f"Validating data completeness for {table_name}")
    
    for column in required_non_null_columns:
        null_count = df[column].isna().sum()
        if null_count > 0:
            raise ValueError(
                f"{table_name}.{column} has {null_count} null values"
            )
    
    logger.info(f"[QUALITY] {table_name} completeness validation passed")
    return True


def run_all_quality_checks(
    client_dim: pd.DataFrame,
    territory_dim: pd.DataFrame,
    assignments_fact: pd.DataFrame
) -> Dict[str, Any]:
    """
    Run all quality checks and return results.
    
    Args:
        client_dim: CLIENT_DIM DataFrame
        territory_dim: TERRITORY_DIM DataFrame
        assignments_fact: ASSIGNMENTS_FACT DataFrame
        
    Returns:
        Dictionary with check results and metrics
    """
    logger.info("Running all quality checks")
    
    results = {
        "passed": True,
        "checks": {},
        "metrics": {}
    }
    
    try:
        # Row count validation
        validate_row_counts(client_dim, territory_dim, assignments_fact)
        results["checks"]["row_counts"] = "PASSED"
        
        # Schema validation
        validate_schema(
            client_dim,
            ["client_key", "client_name", "region", "segment"],
            "CLIENT_DIM"
        )
        results["checks"]["client_dim_schema"] = "PASSED"
        
        validate_schema(
            territory_dim,
            ["territory_id", "region", "segment"],
            "TERRITORY_DIM"
        )
        results["checks"]["territory_dim_schema"] = "PASSED"
        
        validate_schema(
            assignments_fact,
            ["client_key", "territory_id"],
            "ASSIGNMENTS_FACT"
        )
        results["checks"]["assignments_fact_schema"] = "PASSED"
        
        # Referential integrity
        validate_referential_integrity(client_dim, territory_dim, assignments_fact)
        results["checks"]["referential_integrity"] = "PASSED"
        
        # Data completeness
        validate_data_completeness(
            client_dim,
            ["client_key", "client_name"],
            "CLIENT_DIM"
        )
        results["checks"]["client_dim_completeness"] = "PASSED"
        
        # Collect metrics
        results["metrics"] = {
            "client_count": len(client_dim),
            "territory_count": len(territory_dim),
            "assignment_count": len(assignments_fact),
            "active_clients": client_dim["is_active"].sum(),
            "current_assignments": assignments_fact["is_current"].sum()
        }
        
        logger.info("[QUALITY] All quality checks passed ✓")
        
    except Exception as e:
        logger.error(f"[QUALITY] Quality check failed: {e}")
        results["passed"] = False
        results["error"] = str(e)
        raise
    
    return results


