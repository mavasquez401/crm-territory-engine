"""
Region-Based Territory Assignment Rule

Assigns territories based on client region.
This is the primary rule for most territory assignments.
"""

import pandas as pd
import logging

from python_etl.rules_engine.base_rule import BaseRule, RuleResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegionRule(BaseRule):
    """
    Assigns territory based on client's region and segment.
    
    Territory ID format: {REGION_PREFIX}_{SEGMENT_PREFIX}
    Example: NOR_INS (Northeast Institutional)
    
    This rule has medium priority (100) and is typically used
    after whitelist rules but before fallback rules.
    """
    
    def __init__(self, priority: int = 100, enabled: bool = True):
        """
        Initialize region rule.
        
        Args:
            priority: Rule priority (default 100)
            enabled: Whether rule is enabled (default True)
        """
        super().__init__(priority=priority, enabled=enabled)
    
    @property
    def name(self) -> str:
        """Return rule name."""
        return "RegionRule"
    
    def can_evaluate(self, client_record: pd.Series) -> bool:
        """
        Check if client record has required fields.
        
        Args:
            client_record: Client data
            
        Returns:
            True if record has region and segment
        """
        if not super().can_evaluate(client_record):
            return False
        
        # Check for required fields
        has_region = "region" in client_record and pd.notna(client_record["region"])
        has_segment = "segment" in client_record and pd.notna(client_record["segment"])
        
        return has_region and has_segment
    
    def evaluate(self, client_record: pd.Series) -> RuleResult:
        """
        Evaluate region rule for a client.
        
        Args:
            client_record: Client data
            
        Returns:
            RuleResult with territory assignment
        """
        # Get region and segment
        region = str(client_record["region"]).strip()
        segment = str(client_record["segment"]).strip()
        
        # Generate territory ID: First 3 letters of region + first 3 letters of segment
        territory_id = (
            region[:3].upper() + "_" + segment[:3].upper()
        )
        
        # High confidence for region-based assignment
        confidence = 95.0
        
        # Create result
        result = RuleResult(
            territory_id=territory_id,
            confidence=confidence,
            rule_name=self.name,
            metadata={
                "region": region,
                "segment": segment,
                "assignment_method": "region_segment_combination"
            }
        )
        
        logger.debug(
            f"RegionRule assigned {territory_id} for client in {region}/{segment}"
        )
        
        return result


