"""
Segment-Based Territory Assignment Rule

Assigns territories based primarily on client segment.
Used as an alternative or complement to region-based assignment.
"""

import pandas as pd
import logging

from python_etl.rules_engine.base_rule import BaseRule, RuleResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SegmentRule(BaseRule):
    """
    Assigns territory based on client segment.
    
    This rule can be used when region is not available or
    when segment is the primary differentiator.
    
    Priority: 100 (same as RegionRule, but typically used as fallback)
    """
    
    def __init__(self, priority: int = 100, enabled: bool = True):
        """
        Initialize segment rule.
        
        Args:
            priority: Rule priority (default 100)
            enabled: Whether rule is enabled (default True)
        """
        super().__init__(priority=priority, enabled=enabled)
    
    @property
    def name(self) -> str:
        """Return rule name."""
        return "SegmentRule"
    
    def can_evaluate(self, client_record: pd.Series) -> bool:
        """
        Check if client record has segment field.
        
        Args:
            client_record: Client data
            
        Returns:
            True if record has segment
        """
        if not super().can_evaluate(client_record):
            return False
        
        # Check for segment field
        has_segment = "segment" in client_record and pd.notna(client_record["segment"])
        
        return has_segment
    
    def evaluate(self, client_record: pd.Series) -> RuleResult:
        """
        Evaluate segment rule for a client.
        
        Args:
            client_record: Client data
            
        Returns:
            RuleResult with territory assignment
        """
        # Get segment
        segment = str(client_record["segment"]).strip()
        
        # Get region if available for better territory ID
        region = None
        if "region" in client_record and pd.notna(client_record["region"]):
            region = str(client_record["region"]).strip()
        
        # Generate territory ID
        if region:
            # Combine with region if available
            territory_id = (
                region[:3].upper() + "_" + segment[:3].upper()
            )
            confidence = 95.0
        else:
            # Segment-only territory
            territory_id = "GEN_" + segment[:3].upper()
            confidence = 75.0  # Lower confidence without region
        
        # Create result
        result = RuleResult(
            territory_id=territory_id,
            confidence=confidence,
            rule_name=self.name,
            metadata={
                "segment": segment,
                "region": region,
                "assignment_method": "segment_based"
            }
        )
        
        logger.debug(
            f"SegmentRule assigned {territory_id} for client in segment {segment}"
        )
        
        return result

