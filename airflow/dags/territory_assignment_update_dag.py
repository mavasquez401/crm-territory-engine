"""
Territory Assignment Update DAG

Nightly job to re-evaluate territory assignments using the rules engine.
Tracks changes and maintains audit trail.

Schedule: Runs nightly at 2 AM
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Import ETL modules
from python_etl.ingestion import RAW_DIR, CORE_DIR, DATA_DIR
from python_etl.rules_engine.territory_assigner import TerritoryAssigner
from python_etl.rules_engine.assignment_updater import AssignmentUpdater
from python_etl.rules_engine.rules.region_rule import RegionRule
from python_etl.rules_engine.rules.whitelist_rule import WhitelistRule
from python_etl.rules_engine.rules.blacklist_rule import BlacklistRule

# Paths
REPORTS_DIR = DATA_DIR / "reports"
CONFIG_DIR = DATA_DIR / "config"


# -------------------------------------------------------------------
# Task callables
# -------------------------------------------------------------------

def update_assignments_fn():
    """
    Re-evaluate all territory assignments using the rules engine.
    Detects changes and updates assignments with audit trail.
    """
    print("[UPDATE] Starting territory assignment update")
    
    # Initialize territory assigner
    assigner = TerritoryAssigner()
    
    # Add rules in priority order
    # Priority 10: Whitelist (highest priority)
    whitelist_path = CONFIG_DIR / "whitelist.json"
    if whitelist_path.exists():
        assigner.add_rule(WhitelistRule(whitelist_path=whitelist_path))
    
    # Priority 20: Blacklist
    blacklist_path = CONFIG_DIR / "blacklist.json"
    if blacklist_path.exists():
        assigner.add_rule(BlacklistRule(blacklist_path=blacklist_path))
    
    # Priority 100: Region-based assignment (default)
    assigner.add_rule(RegionRule())
    
    print(f"[UPDATE] Configured {len(assigner.get_rules())} rules")
    
    # Initialize assignment updater
    updater = AssignmentUpdater(assigner)
    
    # Define paths
    clients_path = RAW_DIR / "clients.csv"
    current_assignments_path = CORE_DIR / "assignments_fact.csv"
    output_assignments_path = CORE_DIR / "assignments_fact.csv"
    audit_log_path = REPORTS_DIR / "assignment_changes.csv"
    
    # Run update
    summary = updater.run_update(
        clients_path=clients_path,
        current_assignments_path=current_assignments_path,
        output_assignments_path=output_assignments_path,
        audit_log_path=audit_log_path
    )
    
    # Log summary
    print(f"[UPDATE] Update complete")
    print(f"[UPDATE] Total clients: {summary['total_clients']}")
    print(f"[UPDATE] Total changes: {summary['total_changes']}")
    print(f"[UPDATE] Changes by type: {summary['changes_by_type']}")
    
    return summary


# -------------------------------------------------------------------
# DAG definition
# -------------------------------------------------------------------

default_args = {
    "owner": "manuel",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="territory_assignment_update_dag",
    description="Nightly territory assignment update with rules engine",
    default_args=default_args,
    schedule_interval="0 2 * * *",  # Run at 2 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["crm", "territory", "nightly", "rules-engine"],
) as dag:
    
    update_assignments = PythonOperator(
        task_id="update_assignments",
        python_callable=update_assignments_fn,
    )
    
    # Single task for now - can be expanded with pre/post checks
    update_assignments

