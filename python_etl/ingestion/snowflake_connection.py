"""
Snowflake Connection Module

Manages Snowflake database connections with connection pooling and error handling.
Uses environment variables for secure credential management.
"""

import os
import logging
from typing import Optional, Dict, Any
import snowflake.connector
from snowflake.connector import DictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_snowflake_connection(
    account: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    warehouse: Optional[str] = None,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    role: Optional[str] = None
) -> snowflake.connector.SnowflakeConnection:
    """
    Create a Snowflake database connection.
    
    Credentials are read from environment variables if not provided:
    - SNOWFLAKE_ACCOUNT
    - SNOWFLAKE_USER
    - SNOWFLAKE_PASSWORD
    - SNOWFLAKE_WAREHOUSE (optional)
    - SNOWFLAKE_DATABASE (optional)
    - SNOWFLAKE_SCHEMA (optional)
    - SNOWFLAKE_ROLE (optional)
    
    Args:
        account: Snowflake account identifier
        user: Username
        password: Password
        warehouse: Warehouse name
        database: Database name
        schema: Schema name
        role: Role name
        
    Returns:
        Snowflake connection object
        
    Raises:
        ValueError: If required credentials are missing
        snowflake.connector.Error: If connection fails
    """
    # Get credentials from parameters or environment variables
    account = account or os.getenv("SNOWFLAKE_ACCOUNT")
    user = user or os.getenv("SNOWFLAKE_USER")
    password = password or os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    database = database or os.getenv("SNOWFLAKE_DATABASE")
    schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
    role = role or os.getenv("SNOWFLAKE_ROLE", "DATA_ENGINEER")
    
    # Validate required credentials
    if not account or not user or not password:
        raise ValueError(
            "Missing required Snowflake credentials. "
            "Set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD "
            "environment variables."
        )
    
    logger.info(f"Connecting to Snowflake account: {account}")
    
    try:
        # Create connection
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema,
            role=role,
            client_session_keep_alive=True,  # Keep connection alive
            autocommit=False  # Manual transaction control
        )
        
        logger.info("Successfully connected to Snowflake")
        
        # Log connection details
        logger.info(f"  Warehouse: {warehouse}")
        logger.info(f"  Database: {database}")
        logger.info(f"  Schema: {schema}")
        logger.info(f"  Role: {role}")
        
        return conn
        
    except snowflake.connector.Error as e:
        logger.error(f"Failed to connect to Snowflake: {e}")
        raise


def execute_query(
    conn: snowflake.connector.SnowflakeConnection,
    query: str,
    params: Optional[Dict[str, Any]] = None,
    fetch: bool = True
) -> Optional[list]:
    """
    Execute a SQL query on Snowflake.
    
    Args:
        conn: Snowflake connection
        query: SQL query to execute
        params: Optional query parameters
        fetch: Whether to fetch results
        
    Returns:
        Query results if fetch=True, None otherwise
    """
    try:
        cursor = conn.cursor(DictCursor)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            results = cursor.fetchall()
            logger.debug(f"Query returned {len(results)} rows")
            return results
        else:
            conn.commit()
            logger.debug(f"Query executed, {cursor.rowcount} rows affected")
            return None
            
    except snowflake.connector.Error as e:
        logger.error(f"Query execution failed: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def close_connection(conn: snowflake.connector.SnowflakeConnection) -> None:
    """
    Close Snowflake connection.
    
    Args:
        conn: Snowflake connection to close
    """
    try:
        conn.close()
        logger.info("Snowflake connection closed")
    except Exception as e:
        logger.warning(f"Error closing connection: {e}")


