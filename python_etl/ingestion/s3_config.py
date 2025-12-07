"""
AWS S3 Configuration Module

Manages S3 configuration and credentials for data uploads.
"""

import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3Config:
    """
    S3 configuration manager.
    
    Reads configuration from environment variables:
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_REGION
    - S3_BUCKET_NAME
    """
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None
    ):
        """
        Initialize S3 configuration.
        
        Args:
            bucket_name: S3 bucket name
            region: AWS region
            access_key_id: AWS access key ID
            secret_access_key: AWS secret access key
        """
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "institutional-clients-raw")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.access_key_id = access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_access_key = secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        
        # Validate required configuration
        if not self.access_key_id or not self.secret_access_key:
            logger.warning(
                "AWS credentials not found in environment. "
                "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
            )
    
    def is_configured(self) -> bool:
        """
        Check if S3 is properly configured.
        
        Returns:
            True if all required configuration is present
        """
        return bool(
            self.bucket_name and
            self.region and
            self.access_key_id and
            self.secret_access_key
        )
    
    def get_credentials(self) -> dict:
        """
        Get AWS credentials as dictionary.
        
        Returns:
            Dictionary with AWS credentials
        """
        return {
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "region_name": self.region
        }
    
    def __repr__(self) -> str:
        """String representation (hides credentials)."""
        return (
            f"S3Config(bucket={self.bucket_name}, "
            f"region={self.region}, "
            f"configured={self.is_configured()})"
        )


