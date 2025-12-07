"""
Conflict Detection Module

Detects various types of conflicts in territory assignments:
- Territory overlaps (clients assigned to multiple territories)
- Advisor conflicts (advisors assigned to conflicting territories)
- Orphaned assignments (assignments without valid clients/territories)
"""

import pandas as pd
import logging
from typing import Dict, List, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_territory_overlaps(
    assignments_fact: pd.DataFrame,
    client_dim: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Detect clients that could belong to multiple territories.
    
    This checks for:
    - Clients with multiple active assignments
    - Clients that match criteria for multiple territories
    
    Args:
        assignments_fact: ASSIGNMENTS_FACT DataFrame
        client_dim: CLIENT_DIM DataFrame
        
    Returns:
        List of conflicts with details
    """
    logger.info("Detecting territory overlaps")
    
    conflicts = []
    
    # Group assignments by client_key
    client_assignments = assignments_fact.groupby("client_key").agg({
        "territory_id": lambda x: list(x),
        "is_current": "sum"
    }).reset_index()
    
    # Find clients with multiple current assignments
    multiple_assignments = client_assignments[
        client_assignments["is_current"] > 1
    ]
    
    for _, row in multiple_assignments.iterrows():
        client_key = row["client_key"]
        territories = row["territory_id"]
        
        # Get client details
        client_info = client_dim[client_dim["client_key"] == client_key]
        if not client_info.empty:
            client_name = client_info.iloc[0]["client_name"]
        else:
            client_name = "Unknown"
        
        conflicts.append({
            "conflict_type": "TERRITORY_OVERLAP",
            "severity": "WARNING",
            "client_key": client_key,
            "client_name": client_name,
            "territories": territories,
            "message": f"Client {client_name} assigned to multiple territories: {territories}"
        })
    
    logger.info(f"Found {len(conflicts)} territory overlap conflicts")
    return conflicts


def detect_advisor_conflicts(
    assignments_fact: pd.DataFrame,
    territory_dim: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Detect advisors assigned to multiple territories.
    
    This can indicate:
    - Advisors managing clients across territories
    - Potential workload imbalances
    
    Args:
        assignments_fact: ASSIGNMENTS_FACT DataFrame
        territory_dim: TERRITORY_DIM DataFrame
        
    Returns:
        List of conflicts with details
    """
    logger.info("Detecting advisor conflicts")
    
    conflicts = []
    
    # Group by advisor and count unique territories
    advisor_territories = assignments_fact.groupby("primary_advisor_email").agg({
        "territory_id": lambda x: list(set(x)),
        "client_key": "count"
    }).reset_index()
    
    # Find advisors with multiple territories
    multi_territory_advisors = advisor_territories[
        advisor_territories["territory_id"].apply(len) > 1
    ]
    
    for _, row in multi_territory_advisors.iterrows():
        advisor = row["primary_advisor_email"]
        territories = row["territory_id"]
        client_count = row["client_key"]
        
        conflicts.append({
            "conflict_type": "ADVISOR_MULTI_TERRITORY",
            "severity": "INFO",
            "advisor_email": advisor,
            "territories": territories,
            "client_count": client_count,
            "message": f"Advisor {advisor} manages {client_count} clients across {len(territories)} territories"
        })
    
    logger.info(f"Found {len(conflicts)} advisor multi-territory situations")
    return conflicts


def detect_orphaned_assignments(
    assignments_fact: pd.DataFrame,
    client_dim: pd.DataFrame,
    territory_dim: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Detect assignments without valid clients or territories.
    
    This checks for:
    - Assignments with client_key not in CLIENT_DIM
    - Assignments with territory_id not in TERRITORY_DIM
    - Assignments with null values
    
    Args:
        assignments_fact: ASSIGNMENTS_FACT DataFrame
        client_dim: CLIENT_DIM DataFrame
        territory_dim: TERRITORY_DIM DataFrame
        
    Returns:
        List of conflicts with details
    """
    logger.info("Detecting orphaned assignments")
    
    conflicts = []
    
    # Get valid keys
    valid_clients = set(client_dim["client_key"])
    valid_territories = set(territory_dim["territory_id"])
    
    # Check for invalid client keys
    invalid_clients = assignments_fact[
        ~assignments_fact["client_key"].isin(valid_clients)
    ]
    
    for _, row in invalid_clients.iterrows():
        conflicts.append({
            "conflict_type": "ORPHANED_CLIENT",
            "severity": "ERROR",
            "client_key": row["client_key"],
            "territory_id": row["territory_id"],
            "message": f"Assignment references non-existent client: {row['client_key']}"
        })
    
    # Check for invalid territory IDs
    invalid_territories = assignments_fact[
        ~assignments_fact["territory_id"].isin(valid_territories) &
        assignments_fact["territory_id"].notna()
    ]
    
    for _, row in invalid_territories.iterrows():
        conflicts.append({
            "conflict_type": "ORPHANED_TERRITORY",
            "severity": "ERROR",
            "client_key": row["client_key"],
            "territory_id": row["territory_id"],
            "message": f"Assignment references non-existent territory: {row['territory_id']}"
        })
    
    # Check for null values
    null_clients = assignments_fact[assignments_fact["client_key"].isna()]
    null_territories = assignments_fact[assignments_fact["territory_id"].isna()]
    
    for _, row in null_clients.iterrows():
        conflicts.append({
            "conflict_type": "NULL_CLIENT",
            "severity": "ERROR",
            "territory_id": row["territory_id"],
            "message": "Assignment has null client_key"
        })
    
    for _, row in null_territories.iterrows():
        conflicts.append({
            "conflict_type": "NULL_TERRITORY",
            "severity": "WARNING",
            "client_key": row["client_key"],
            "message": f"Client {row['client_key']} has null territory assignment"
        })
    
    logger.info(f"Found {len(conflicts)} orphaned assignment conflicts")
    return conflicts


def generate_conflict_report(
    conflicts: List[Dict[str, Any]],
    output_path: Path = None
) -> pd.DataFrame:
    """
    Generate a detailed conflict report.
    
    Args:
        conflicts: List of conflicts
        output_path: Optional path to save report
        
    Returns:
        DataFrame containing conflict report
    """
    logger.info("Generating conflict report")
    
    if not conflicts:
        logger.info("No conflicts found - clean data!")
        return pd.DataFrame()
    
    # Convert to DataFrame
    report_df = pd.DataFrame(conflicts)
    
    # Count by severity
    severity_counts = report_df["severity"].value_counts().to_dict()
    
    logger.info("Conflict Summary:")
    for severity, count in severity_counts.items():
        logger.info(f"  {severity}: {count}")
    
    # Log critical errors
    errors = report_df[report_df["severity"] == "ERROR"]
    if not errors.empty:
        logger.error(f"Found {len(errors)} ERROR-level conflicts:")
        for _, conflict in errors.head(5).iterrows():
            logger.error(f"  {conflict['message']}")
    
    # Save to file if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(output_path, index=False)
        logger.info(f"Conflict report saved to: {output_path}")
    
    return report_df


def detect_all_conflicts(
    client_dim: pd.DataFrame,
    territory_dim: pd.DataFrame,
    assignments_fact: pd.DataFrame,
    report_path: Path = None
) -> Dict[str, Any]:
    """
    Run all conflict detection checks.
    
    Args:
        client_dim: CLIENT_DIM DataFrame
        territory_dim: TERRITORY_DIM DataFrame
        assignments_fact: ASSIGNMENTS_FACT DataFrame
        report_path: Optional path to save conflict report
        
    Returns:
        Dictionary with conflict results
    """
    logger.info("Running all conflict detection checks")
    
    all_conflicts = []
    
    # Detect territory overlaps
    territory_conflicts = detect_territory_overlaps(assignments_fact, client_dim)
    all_conflicts.extend(territory_conflicts)
    
    # Detect advisor conflicts
    advisor_conflicts = detect_advisor_conflicts(assignments_fact, territory_dim)
    all_conflicts.extend(advisor_conflicts)
    
    # Detect orphaned assignments
    orphaned_conflicts = detect_orphaned_assignments(
        assignments_fact,
        client_dim,
        territory_dim
    )
    all_conflicts.extend(orphaned_conflicts)
    
    # Generate report
    report_df = generate_conflict_report(all_conflicts, output_path=report_path)
    
    # Prepare results
    results = {
        "total_conflicts": len(all_conflicts),
        "conflicts_by_type": {},
        "conflicts_by_severity": {},
        "has_errors": False
    }
    
    if all_conflicts:
        results["conflicts_by_type"] = pd.DataFrame(all_conflicts)["conflict_type"].value_counts().to_dict()
        results["conflicts_by_severity"] = pd.DataFrame(all_conflicts)["severity"].value_counts().to_dict()
        results["has_errors"] = "ERROR" in results["conflicts_by_severity"]
    
    logger.info(f"Conflict detection complete. Total conflicts: {len(all_conflicts)}")
    
    return results


