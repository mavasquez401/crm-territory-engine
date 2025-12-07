"""
Assignment Updater Module

Re-evaluates territory assignments using the rules engine.
Tracks changes and maintains audit trail.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from python_etl.rules_engine.territory_assigner import TerritoryAssigner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssignmentUpdater:
    """
    Updates territory assignments by re-evaluating rules.
    
    Tracks changes and maintains audit trail for compliance.
    """
    
    def __init__(self, assigner: TerritoryAssigner):
        """
        Initialize assignment updater.
        
        Args:
            assigner: Configured TerritoryAssigner with rules
        """
        self.assigner = assigner
        self.changes: List[Dict[str, Any]] = []
    
    def load_current_assignments(
        self,
        assignments_path: Path
    ) -> pd.DataFrame:
        """
        Load current assignments from file.
        
        Args:
            assignments_path: Path to assignments CSV
            
        Returns:
            DataFrame with current assignments
        """
        logger.info(f"Loading current assignments from {assignments_path}")
        
        if not assignments_path.exists():
            logger.warning("No existing assignments found")
            return pd.DataFrame()
        
        assignments = pd.read_csv(assignments_path)
        logger.info(f"Loaded {len(assignments)} current assignments")
        
        return assignments
    
    def load_clients(self, clients_path: Path) -> pd.DataFrame:
        """
        Load client data for re-evaluation.
        
        Args:
            clients_path: Path to clients CSV
            
        Returns:
            DataFrame with client data
        """
        logger.info(f"Loading clients from {clients_path}")
        clients = pd.read_csv(clients_path)
        logger.info(f"Loaded {len(clients)} clients")
        return clients
    
    def re_evaluate_assignments(
        self,
        clients_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Re-evaluate territory assignments for all clients.
        
        Args:
            clients_df: DataFrame with client data
            
        Returns:
            DataFrame with new assignments
        """
        logger.info("Re-evaluating territory assignments")
        
        # Use territory assigner to assign territories
        new_assignments = self.assigner.assign_territories_bulk(clients_df)
        
        logger.info("Re-evaluation complete")
        return new_assignments
    
    def detect_changes(
        self,
        old_assignments: pd.DataFrame,
        new_assignments: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Detect changes between old and new assignments.
        
        Args:
            old_assignments: Previous assignments
            new_assignments: New assignments
            
        Returns:
            List of changes with details
        """
        logger.info("Detecting assignment changes")
        
        changes = []
        
        # Handle case where old_assignments is empty
        if old_assignments.empty:
            logger.info("No previous assignments - all assignments are new")
            for _, row in new_assignments.iterrows():
                if pd.notna(row.get("assigned_territory_id")):
                    changes.append({
                        "client_id": row.get("client_id"),
                        "client_name": row.get("client_name"),
                        "change_type": "NEW",
                        "old_territory": None,
                        "new_territory": row.get("assigned_territory_id"),
                        "rule": row.get("assignment_rule"),
                        "timestamp": datetime.now().isoformat()
                    })
            return changes
        
        # Create lookup dictionaries
        old_lookup = {}
        if "client_key" in old_assignments.columns:
            old_lookup = dict(zip(
                old_assignments["client_key"],
                old_assignments["territory_id"]
            ))
        elif "client_id" in old_assignments.columns:
            old_lookup = dict(zip(
                old_assignments["client_id"],
                old_assignments["territory_id"]
            ))
        
        # Check each new assignment
        for _, row in new_assignments.iterrows():
            client_id = row.get("client_id") or row.get("client_key")
            new_territory = row.get("assigned_territory_id")
            old_territory = old_lookup.get(client_id)
            
            # Detect change type
            if old_territory is None and pd.notna(new_territory):
                change_type = "NEW"
            elif pd.isna(new_territory) and old_territory is not None:
                change_type = "REMOVED"
            elif old_territory != new_territory:
                change_type = "CHANGED"
            else:
                continue  # No change
            
            changes.append({
                "client_id": client_id,
                "client_name": row.get("client_name"),
                "change_type": change_type,
                "old_territory": old_territory,
                "new_territory": new_territory,
                "rule": row.get("assignment_rule"),
                "timestamp": datetime.now().isoformat()
            })
        
        logger.info(f"Detected {len(changes)} changes")
        
        # Log change summary
        if changes:
            change_types = pd.DataFrame(changes)["change_type"].value_counts().to_dict()
            logger.info(f"Change summary: {change_types}")
        
        return changes
    
    def update_assignments(
        self,
        new_assignments: pd.DataFrame,
        output_path: Path
    ) -> None:
        """
        Write updated assignments to file.
        
        Args:
            new_assignments: DataFrame with new assignments
            output_path: Path to write assignments
        """
        logger.info(f"Writing updated assignments to {output_path}")
        
        # Prepare assignments fact table format
        assignments_fact = new_assignments[[
            "client_id",
            "assigned_territory_id",
            "primary_advisor_email"
        ]].copy()
        
        # Rename columns to match fact table schema
        assignments_fact.columns = [
            "client_key",
            "territory_id",
            "primary_advisor_email"
        ]
        
        # Add metadata columns
        assignments_fact["assignment_type"] = "PRIMARY"
        assignments_fact["is_current"] = True
        assignments_fact["updated_at"] = datetime.now().isoformat()
        assignments_fact["updated_by_rule"] = new_assignments["assignment_rule"]
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        assignments_fact.to_csv(output_path, index=False)
        
        logger.info(f"Wrote {len(assignments_fact)} assignments")
    
    def save_audit_log(
        self,
        changes: List[Dict[str, Any]],
        audit_path: Path
    ) -> None:
        """
        Save audit log of changes.
        
        Args:
            changes: List of changes
            audit_path: Path to save audit log
        """
        if not changes:
            logger.info("No changes to log")
            return
        
        logger.info(f"Saving audit log to {audit_path}")
        
        # Convert to DataFrame
        changes_df = pd.DataFrame(changes)
        
        # Append to existing audit log if it exists
        if audit_path.exists():
            existing_log = pd.read_csv(audit_path)
            changes_df = pd.concat([existing_log, changes_df], ignore_index=True)
        
        # Write audit log
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        changes_df.to_csv(audit_path, index=False)
        
        logger.info(f"Saved {len(changes)} changes to audit log")
    
    def run_update(
        self,
        clients_path: Path,
        current_assignments_path: Path,
        output_assignments_path: Path,
        audit_log_path: Path
    ) -> Dict[str, Any]:
        """
        Run complete assignment update process.
        
        Args:
            clients_path: Path to client data
            current_assignments_path: Path to current assignments
            output_assignments_path: Path to write new assignments
            audit_log_path: Path to save audit log
            
        Returns:
            Dictionary with update summary
        """
        logger.info("Starting assignment update process")
        
        # Load data
        clients = self.load_clients(clients_path)
        old_assignments = self.load_current_assignments(current_assignments_path)
        
        # Re-evaluate assignments
        new_assignments = self.re_evaluate_assignments(clients)
        
        # Detect changes
        changes = self.detect_changes(old_assignments, new_assignments)
        
        # Update assignments
        self.update_assignments(new_assignments, output_assignments_path)
        
        # Save audit log
        self.save_audit_log(changes, audit_log_path)
        
        # Prepare summary
        summary = {
            "total_clients": len(clients),
            "total_changes": len(changes),
            "changes_by_type": {},
            "timestamp": datetime.now().isoformat()
        }
        
        if changes:
            summary["changes_by_type"] = pd.DataFrame(changes)["change_type"].value_counts().to_dict()
        
        logger.info("Assignment update complete")
        logger.info(f"Summary: {summary}")
        
        return summary


