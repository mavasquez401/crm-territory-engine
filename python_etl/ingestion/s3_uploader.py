"""
AWS S3 Uploader Module

Uploads files to S3 with timestamped paths and error handling.
"""

import boto3
from botocore.exceptions import ClientError
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from python_etl.ingestion.s3_config import S3Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_to_s3(
    file_path: Path,
    s3_key: Optional[str] = None,
    config: Optional[S3Config] = None
) -> str:
    """
    Upload file to S3 with timestamped path.
    
    Args:
        file_path: Local file path to upload
        s3_key: S3 object key (path in bucket). If None, generates timestamped path.
        config: S3Config object. If None, creates from environment.
        
    Returns:
        S3 URI of uploaded file (s3://bucket/key)
        
    Raises:
        FileNotFoundError: If local file doesn't exist
        ClientError: If S3 upload fails
    """
    # Validate file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get configuration
    if config is None:
        config = S3Config()
    
    if not config.is_configured():
        raise ValueError("S3 not properly configured. Check environment variables.")
    
    # Generate S3 key if not provided
    if s3_key is None:
        # Format: YYYY/MM/DD/filename.csv
        now = datetime.now()
        s3_key = f"{now.year}/{now.month:02d}/{now.day:02d}/{file_path.name}"
    
    logger.info(f"Uploading {file_path} to s3://{config.bucket_name}/{s3_key}")
    
    try:
        # Create S3 client
        s3_client = boto3.client('s3', **config.get_credentials())
        
        # Upload file
        s3_client.upload_file(
            str(file_path),
            config.bucket_name,
            s3_key,
            ExtraArgs={'ServerSideEncryption': 'AES256'}  # Encrypt at rest
        )
        
        # Construct S3 URI
        s3_uri = f"s3://{config.bucket_name}/{s3_key}"
        
        logger.info(f"Successfully uploaded to {s3_uri}")
        
        return s3_uri
        
    except ClientError as e:
        logger.error(f"Failed to upload to S3: {e}")
        raise


def verify_upload(s3_uri: str, config: Optional[S3Config] = None) -> bool:
    """
    Verify that file exists in S3.
    
    Args:
        s3_uri: S3 URI to verify (s3://bucket/key)
        config: S3Config object
        
    Returns:
        True if file exists
    """
    # Parse S3 URI
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Invalid S3 URI: {s3_uri}")
    
    parts = s3_uri[5:].split("/", 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else ""
    
    # Get configuration
    if config is None:
        config = S3Config()
    
    try:
        s3_client = boto3.client('s3', **config.get_credentials())
        s3_client.head_object(Bucket=bucket, Key=key)
        logger.info(f"Verified: {s3_uri} exists")
        return True
    except ClientError:
        logger.warning(f"File not found: {s3_uri}")
        return False

