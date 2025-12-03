from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

# Project root: .../crm-territory-engine
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "mock_clients"
CORE_DIR = DATA_DIR / "core"
CORE_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------------
# Task callables
# -------------------------------------------------------------------

def extract_clients_fn():
    """
    Simulate extracting clients from a source system into RAW.
    For now we just read the CSV and log a few rows.
    """
    csv_path = RAW_DIR / "clients.csv"
    print(f"Reading clients from: {csv_path}")

    df = pd.read_csv(csv_path)
    print("Sample extracted rows:")
    print(df.head(3).to_string(index=False))


def load_raw_to_snowflake_fn():
    """
    In a real pipeline this would load RAW.CLIENTS into Snowflake.
    For now we just log what we *would* do.
    """
    csv_path = RAW_DIR / "clients.csv"
    df = pd.read_csv(csv_path)
    row_count = len(df)
    print(f"[SIMULATION] Would load {row_count} clients into Snowflake RAW.CLIENTS.")


def transform_to_core_fn():
    """
    Build simple CORE dimension/fact tables from RAW clients
    and write them as CSVs into data/core/.
    """
    clients_path = RAW_DIR / "clients.csv"
    print(f"Transforming RAW clients from: {clients_path}")

    clients = pd.read_csv(clients_path)

    # ---------------- CLIENT_DIM ----------------
    client_dim = clients.rename(
        columns={
            "client_id": "client_key",
            "client_name": "client_name",
            "region": "region",
            "segment": "segment",
            "parent_org": "parent_org",
            "advisor_email": "primary_advisor_email",
        }
    ).copy()
    client_dim["is_active"] = True

    # ---------------- TERRITORY_DIM ----------------
    territory_dim = (
        client_dim[["region", "segment"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    territory_dim["territory_id"] = (
        territory_dim["region"].str[:3].str.upper()
        + "_"
        + territory_dim["segment"].str[:3].str.upper()
    )
    territory_dim["owner_role"] = "Sales Rep"

    # ---------------- ASSIGNMENTS_FACT ----------------
    assignments_fact = client_dim.merge(
        territory_dim,
        on=["region", "segment"],
        how="left",
    )[["client_key", "territory_id", "primary_advisor_email"]]

    assignments_fact["assignment_type"] = "PRIMARY"
    assignments_fact["is_current"] = True

    # ---------------- WRITE OUT ----------------
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


def quality_checks_fn():
    """
    Basic placeholder data quality checks on the CORE outputs.
    """
    client_dim = pd.read_csv(CORE_DIR / "client_dim.csv")
    territory_dim = pd.read_csv(CORE_DIR / "territory_dim.csv")
    assignments_fact = pd.read_csv(CORE_DIR / "assignments_fact.csv")

    print(f"[QUALITY] client_dim rows: {len(client_dim)}")
    print(f"[QUALITY] territory_dim rows: {len(territory_dim)}")
    print(f"[QUALITY] assignments_fact rows: {len(assignments_fact)}")

    assert len(client_dim) > 0, "client_dim should not be empty"
    assert len(territory_dim) > 0, "territory_dim should not be empty"
    assert len(assignments_fact) > 0, "assignments_fact should not be empty"
    print("[QUALITY] Basic row-count checks passed.")


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
    description="Demo CRM client ingestion -> RAW -> CORE -> QA",
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

    load_raw_to_snowflake = PythonOperator(
        task_id="load_raw_to_snowflake",
        python_callable=load_raw_to_snowflake_fn,
    )

    transform_to_core = PythonOperator(
        task_id="transform_to_core",
        python_callable=transform_to_core_fn,
    )

    quality_checks = PythonOperator(
        task_id="quality_checks",
        python_callable=quality_checks_fn,
    )

    # Task dependencies
    extract_clients >> load_raw_to_snowflake >> transform_to_core >> quality_checks