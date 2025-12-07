"""
Snowflake Transformation Module

Executes transformations in Snowflake using SQL.
More efficient than pandas for large datasets.
"""

import logging
from pathlib import Path
from typing import Optional
import snowflake.connector

from python_etl.ingestion.snowflake_connection import get_snowflake_connection, execute_query, close_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_transformation_sql(
    sql_file_path: Path,
    database: str = "CORE",
    schema: str = "dimensional"
) -> None:
    """
    Execute SQL transformation script in Snowflake.
    
    Args:
        sql_file_path: Path to SQL file
        database: Target database
        schema: Target schema
    """
    logger.info(f"Running transformation: {sql_file_path}")
    
    # Read SQL file
    if not sql_file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")
    
    with open(sql_file_path, 'r') as f:
        sql_script = f.read()
    
    # Get connection
    conn = get_snowflake_connection(database=database, schema=schema)
    
    try:
        # Split script into individual statements
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        logger.info(f"Executing {len(statements)} SQL statements")
        
        for i, statement in enumerate(statements, 1):
            # Skip comments
            if statement.startswith('--') or statement.startswith('/*'):
                continue
            
            logger.debug(f"Executing statement {i}/{len(statements)}")
            execute_query(conn, statement, fetch=False)
        
        conn.commit()
        logger.info("Transformation complete")
        
    except snowflake.connector.Error as e:
        logger.error(f"Transformation failed: {e}")
        conn.rollback()
        raise
    finally:
        close_connection(conn)


def transform_raw_to_core() -> None:
    """
    Execute the main RAW to CORE transformation.
    Runs the transform_to_core.sql script.
    """
    from python_etl.ingestion import PROJECT_ROOT
    
    sql_file = PROJECT_ROOT / "infrastructure" / "snowflake" / "transformations" / "transform_to_core.sql"
    
    logger.info("Starting RAW to CORE transformation")
    run_transformation_sql(sql_file, database="CORE", schema="dimensional")
    logger.info("RAW to CORE transformation complete")


