"""
Snowflake Data Loader Module

Loads data from CSV files into Snowflake RAW tables using COPY INTO command.
Handles file format configuration and error logging.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional
import snowflake.connector

from python_etl.ingestion.snowflake_connection import get_snowflake_connection, close_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_csv_to_raw(
    csv_path: Path,
    table_name: str = "CLIENTS",
    database: str = "RAW",
    schema: str = "client_hierarchy",
    truncate: bool = False
) -> int:
    """
    Load CSV file into Snowflake RAW table using COPY INTO.
    
    Args:
        csv_path: Path to CSV file
        table_name: Target table name
        database: Target database
        schema: Target schema
        truncate: Whether to truncate table before loading
        
    Returns:
        Number of rows loaded
    """
    logger.info(f"Loading {csv_path} to {database}.{schema}.{table_name}")
    
    # Validate file exists
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Get connection
    conn = get_snowflake_connection(database=database, schema=schema)
    
    try:
        cursor = conn.cursor()
        
        # Truncate table if requested
        if truncate:
            logger.info(f"Truncating table {table_name}")
            cursor.execute(f"TRUNCATE TABLE IF EXISTS {table_name}")
        
        # Create file format for CSV
        file_format_sql = """
        CREATE OR REPLACE FILE FORMAT csv_format
            TYPE = 'CSV'
            FIELD_DELIMITER = ','
            SKIP_HEADER = 1
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            NULL_IF = ('NULL', 'null', '')
            EMPTY_FIELD_AS_NULL = TRUE
            COMPRESSION = 'NONE'
        """
        cursor.execute(file_format_sql)
        logger.info("Created CSV file format")
        
        # Put file into Snowflake stage
        put_sql = f"PUT file://{csv_path} @%{table_name}"
        cursor.execute(put_sql)
        logger.info("Uploaded file to Snowflake stage")
        
        # Copy data from stage to table
        copy_sql = f"""
        COPY INTO {table_name}
        FROM @%{table_name}
        FILE_FORMAT = (FORMAT_NAME = 'csv_format')
        ON_ERROR = 'CONTINUE'
        PURGE = TRUE
        """
        cursor.execute(copy_sql)
        
        # Get row count
        result = cursor.fetchone()
        rows_loaded = result[0] if result else 0
        
        conn.commit()
        
        logger.info(f"Successfully loaded {rows_loaded} rows into {table_name}")
        
        return rows_loaded
        
    except snowflake.connector.Error as e:
        logger.error(f"Failed to load data: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        close_connection(conn)


def load_dataframe_to_raw(
    df: pd.DataFrame,
    table_name: str = "CLIENTS",
    database: str = "RAW",
    schema: str = "client_hierarchy",
    truncate: bool = False
) -> int:
    """
    Load pandas DataFrame directly into Snowflake RAW table.
    
    Args:
        df: DataFrame to load
        table_name: Target table name
        database: Target database
        schema: Target schema
        truncate: Whether to truncate table before loading
        
    Returns:
        Number of rows loaded
    """
    logger.info(f"Loading DataFrame ({len(df)} rows) to {database}.{schema}.{table_name}")
    
    # Get connection
    conn = get_snowflake_connection(database=database, schema=schema)
    
    try:
        cursor = conn.cursor()
        
        # Truncate table if requested
        if truncate:
            logger.info(f"Truncating table {table_name}")
            cursor.execute(f"TRUNCATE TABLE IF EXISTS {table_name}")
        
        # Use pandas write_pandas method (more efficient)
        from snowflake.connector.pandas_tools import write_pandas
        
        success, num_chunks, num_rows, output = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name,
            database=database,
            schema=schema,
            auto_create_table=False,  # Table should already exist
            overwrite=truncate
        )
        
        if success:
            logger.info(f"Successfully loaded {num_rows} rows into {table_name}")
            return num_rows
        else:
            raise Exception(f"Failed to load data: {output}")
            
    except Exception as e:
        logger.error(f"Failed to load DataFrame: {e}")
        conn.rollback()
        raise
    finally:
        close_connection(conn)


