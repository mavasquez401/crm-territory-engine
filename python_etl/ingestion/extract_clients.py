"""
Client Data Extraction Module

Extracts client data from various sources (CSV, API, database).
Handles error cases and provides logging for monitoring.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_clients_from_csv(
    csv_path: Path,
    encoding: str = "utf-8",
    validate: bool = True
) -> pd.DataFrame:
    """
    Extract client data from a CSV file.
    
    Args:
        csv_path: Path to the CSV file
        encoding: File encoding (default: utf-8)
        validate: Whether to validate required columns
        
    Returns:
        DataFrame containing client data
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
    logger.info(f"Extracting clients from: {csv_path}")
    
    # Check if file exists
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_path, encoding=encoding)
        logger.info(f"Successfully read {len(df)} rows from CSV")
        
        # Validate required columns
        if validate:
            required_columns = [
                "client_id",
                "client_name",
                "region",
                "segment",
                "parent_org",
                "advisor_email"
            ]
            missing_columns = set(required_columns) - set(df.columns)
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            logger.info("Column validation passed")
        
        # Log sample data
        logger.info("Sample extracted rows:")
        logger.info(f"\n{df.head(3).to_string(index=False)}")
        
        return df
        
    except pd.errors.EmptyDataError:
        logger.error(f"CSV file is empty: {csv_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise


def extract_clients_from_api(
    api_url: str,
    api_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Extract client data from an external API.
    
    Args:
        api_url: URL of the API endpoint
        api_key: Optional API key for authentication
        
    Returns:
        DataFrame containing client data
        
    Note:
        This is a placeholder for future API integration.
    """
    logger.info(f"API extraction not yet implemented for: {api_url}")
    raise NotImplementedError("API extraction will be implemented in future version")


def extract_clients(
    source_type: str = "csv",
    source_path: Optional[Path] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Main extraction function that routes to appropriate extractor.
    
    Args:
        source_type: Type of source ("csv", "api", "database")
        source_path: Path to source file (for CSV)
        **kwargs: Additional arguments for specific extractors
        
    Returns:
        DataFrame containing client data
    """
    if source_type == "csv":
        if source_path is None:
            raise ValueError("source_path required for CSV extraction")
        return extract_clients_from_csv(source_path, **kwargs)
    elif source_type == "api":
        raise NotImplementedError("API extraction not yet implemented")
    elif source_type == "database":
        raise NotImplementedError("Database extraction not yet implemented")
    else:
        raise ValueError(f"Unknown source type: {source_type}")

