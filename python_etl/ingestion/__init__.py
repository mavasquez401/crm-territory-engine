"""
Data Ingestion Module

Handles extraction of client data from various sources including:
- CSV files
- S3 buckets
- Snowflake databases
- External APIs
"""

from pathlib import Path

# Project root directory for path resolution
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "mock_clients"
CORE_DIR = DATA_DIR / "core"

