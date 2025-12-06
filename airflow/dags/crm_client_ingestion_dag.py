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
from python_etl.ingestion.extract_clients import extract_clients_from_csv
from python_etl.transformations.dimensional_model import transform_to_dimensional_model
from python_etl.transformations.quality_checks import run_all_quality_checks
from python_etl.transformations.conflict_detection import detect_all_conflicts
from python_etl.dedupe.deduplication_pipeline import run_deduplication_pipeline

# Ensure directories exist
CORE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = DATA_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------------
# Task callables
# -------------------------------------------------------------------

def extract_clients_fn():
    """
    Extract clients from CSV source.
    Uses modular extraction function from python_etl.ingestion.
    """
    csv_path = RAW_DIR / "clients.csv"
    df = extract_clients_from_csv(csv_path)
    return df


def deduplicate_clients_fn():
    """
    Identify and handle duplicate client records using fuzzy matching.
    Generates a deduplication report for review.
    """
    # Read extracted data
    csv_path = RAW_DIR / "clients.csv"
    df = extract_clients_from_csv(csv_path, validate=False)
    
    # Run deduplication pipeline
    # Using "manual" strategy to flag duplicates without auto-merging
    # This allows for manual review of potential duplicates
    report_path = REPORTS_DIR / "duplicates_report.csv"
    df_deduped = run_deduplication_pipeline(
        df,
        threshold=85.0,
        merge_strategy="manual",  # Flag for review, don't auto-merge
        report_path=report_path
    )
    
    print(f"Deduplication complete. Report saved to: {report_path}")
    return df_deduped


def load_raw_to_snowflake_fn():
    """
    Load extracted data to Snowflake RAW layer.
    Currently simulated - will be replaced with real Snowflake integration.
    """
    csv_path = RAW_DIR / "clients.csv"
    df = extract_clients_from_csv(csv_path, validate=False)
    row_count = len(df)
    print(f"[SIMULATION] Would load {row_count} clients into Snowflake RAW.CLIENTS.")


def transform_to_core_fn():
    """
    Transform RAW data to CORE dimensional model.
    Uses modular transformation functions from python_etl.transformations.
    """
    # Read raw data
    csv_path = RAW_DIR / "clients.csv"
    raw_clients = extract_clients_from_csv(csv_path, validate=False)
    
    # Transform to dimensional model
    client_dim, territory_dim, assignments_fact = transform_to_dimensional_model(raw_clients)
    
    # Write to CSV files
    client_dim_path = CORE_DIR / "client_dim.csv"
    territory_dim_path = CORE_DIR / "territory_dim.csv"
    assignments_fact_path = CORE_DIR / "assignments_fact.csv"
    
    client_dim.to_csv(client_dim_path, index=False)
    territory_dim.to_csv(territory_dim_path, index=False)
    assignments_fact.to_csv(assignments_fact_path, index=False)
    
    print(f"Wrote CORE tables to {CORE_DIR}")
    print(f"- {client_dim_path}")
    print(f"- {territory_dim_path}")
    print(f"- {assignments_fact_path}")


def detect_conflicts_fn():
    """
    Detect conflicts in territory assignments.
    Identifies overlaps, advisor conflicts, and orphaned assignments.
    """
    import pandas as pd
    
    # Read CORE tables
    client_dim = pd.read_csv(CORE_DIR / "client_dim.csv")
    territory_dim = pd.read_csv(CORE_DIR / "territory_dim.csv")
    assignments_fact = pd.read_csv(CORE_DIR / "assignments_fact.csv")
    
    # Run conflict detection
    report_path = REPORTS_DIR / "conflicts_report.csv"
    results = detect_all_conflicts(
        client_dim,
        territory_dim,
        assignments_fact,
        report_path=report_path
    )
    
    # Log results
    print(f"[CONFLICTS] Total conflicts: {results['total_conflicts']}")
    if results['has_errors']:
        print("[CONFLICTS] WARNING: Error-level conflicts detected!")
    
    return results


def quality_checks_fn():
    """
    Run comprehensive data quality checks.
    Uses modular quality check functions from python_etl.transformations.
    """
    import pandas as pd
    
    # Read CORE tables
    client_dim = pd.read_csv(CORE_DIR / "client_dim.csv")
    territory_dim = pd.read_csv(CORE_DIR / "territory_dim.csv")
    assignments_fact = pd.read_csv(CORE_DIR / "assignments_fact.csv")
    
    # Run all quality checks
    results = run_all_quality_checks(client_dim, territory_dim, assignments_fact)
    
    # Log results
    print(f"[QUALITY] All checks passed: {results['passed']}")
    print(f"[QUALITY] Metrics: {results['metrics']}")


# -------------------------------------------------------------------
# DAG definition
# -------------------------------------------------------------------

default_args = {
    "owner": "manuel",
    "depends_on_past": False,
    "retries": 0,
}

with DAG(
    dag_id="crm_client_ingestion_dag",
    description="CRM client ingestion with deduplication -> RAW -> CORE -> QA",
    default_args=default_args,
    schedule_interval=None,  # run manually for now
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["crm", "territory", "demo"],
) as dag:
    extract_clients = PythonOperator(
        task_id="extract_clients",
        python_callable=extract_clients_fn,
    )

    deduplicate_clients = PythonOperator(
        task_id="deduplicate_clients",
        python_callable=deduplicate_clients_fn,
    )

    load_raw_to_snowflake = PythonOperator(
        task_id="load_raw_to_snowflake",
        python_callable=load_raw_to_snowflake_fn,
    )

    transform_to_core = PythonOperator(
        task_id="transform_to_core",
        python_callable=transform_to_core_fn,
    )

    detect_conflicts = PythonOperator(
        task_id="detect_conflicts",
        python_callable=detect_conflicts_fn,
    )

    quality_checks = PythonOperator(
        task_id="quality_checks",
        python_callable=quality_checks_fn,
    )

    # Task dependencies
    extract_clients >> deduplicate_clients >> load_raw_to_snowflake >> transform_to_core >> detect_conflicts >> quality_checks