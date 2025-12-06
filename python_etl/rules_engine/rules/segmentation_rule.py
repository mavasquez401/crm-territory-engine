"""
Auto-Segmentation Tier Rule

Assigns clients to territory tiers based on client attributes.
Supports tiered territory assignment (Tier 1, Tier 2, Tier 3).
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from python_etl.rules_engine.base_rule import BaseRule, RuleResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SegmentationRule(BaseRule):
    """
    Assigns territories based on client segmentation tiers.
    
    Tiers are defined by client attributes (e.g., revenue, size, type).
    Each tier maps to specific territories with appropriate advisor capacity.
    
    Configuration format (JSON):
    {
        "tiers": {
            "tier_1": {
                "criteria": {"segment": "Institutional", "min_revenue": 1000000},
                "territory_suffix": "T1",
                "priority": 1
            },
            "tier_2": {
                "criteria": {"segment": "Retail", "min_revenue": 100000},
                "territory_suffix": "T2",
                "priority": 2
            }
        }
    }
    
    Priority: 50 (after whitelist/blacklist, before region/segment)
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        priority: int = 50,
        enabled: bool = True
    ):
        """
        Initialize segmentation rule.
        
        Args:
            config_path: Path to JSON configuration file
            config_dict: Configuration dictionary
            priority: Rule priority (default 50)
            enabled: Whether rule is enabled (default True)
        """
        super().__init__(priority=priority, enabled=enabled)
        self.config: Dict[str, Any] = {}
        
        # Load configuration
        if config_path:
            self.load_from_file(config_path)
        elif config_dict:
            self.config = config_dict
        
        logger.info(f"SegmentationRule initialized with {len(self.config.get('tiers', {}))} tiers")
    
    @property
    def name(self) -> str:
        """Return rule name."""
        return "SegmentationRule"
    
    def load_from_file(self, file_path: Path) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            file_path: Path to JSON file
        """
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded segmentation config from {file_path}")
            else:
                logger.warning(f"Config file not found: {file_path}")
                self.config = {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = {}
    
    def evaluate_tier(self, client_record: pd.Series, tier_config: Dict[str, Any]) -> bool:
        """
        Check if client matches tier criteria.
        
        Args:
            client_record: Client data
            tier_config: Tier configuration with criteria
            
        Returns:
            True if client matches all criteria
        """
        criteria = tier_config.get("criteria", {})
        
        for field, expected_value in criteria.items():
            # Handle different criteria types
            if field.startswith("min_"):
                # Minimum value check
                actual_field = field.replace("min_", "")
                if actual_field not in client_record:
                    return False
                if pd.isna(client_record[actual_field]):
                    return False
                if client_record[actual_field] < expected_value:
                    return False
            
            elif field.startswith("max_"):
                # Maximum value check
                actual_field = field.replace("max_", "")
                if actual_field not in client_record:
                    return False
                if pd.isna(client_record[actual_field]):
                    return False
                if client_record[actual_field] > expected_value:
                    return False
            
            else:
                # Exact match check
                if field not in client_record:
                    return False
                if pd.isna(client_record[field]):
                    return False
                if client_record[field] != expected_value:
                    return False
        
        return True
    
    def can_evaluate(self, client_record: pd.Series) -> bool:
        """
        Check if rule can evaluate this client.
        
        Args:
            client_record: Client data
            
        Returns:
            True if configuration is loaded
        """
        if not super().can_evaluate(client_record):
            return False
        
        return "tiers" in self.config and len(self.config["tiers"]) > 0
    
    def evaluate(self, client_record: pd.Series) -> RuleResult:
        """
        Evaluate segmentation rule for a client.
        
        Args:
            client_record: Client data
            
        Returns:
            RuleResult with tier-based territory assignment
        """
        tiers = self.config.get("tiers", {})
        
        # Sort tiers by priority
        sorted_tiers = sorted(
            tiers.items(),
            key=lambda x: x[1].get("priority", 999)
        )
        
        # Find first matching tier
        for tier_name, tier_config in sorted_tiers:
            if self.evaluate_tier(client_record, tier_config):
                # Get territory suffix for this tier
                suffix = tier_config.get("territory_suffix", "")
                
                # Build territory ID with tier suffix
                if "region" in client_record and "segment" in client_record:
                    region = str(client_record["region"])[:3].upper()
                    segment = str(client_record["segment"])[:3].upper()
                    territory_id = f"{region}_{segment}_{suffix}" if suffix else f"{region}_{segment}"
                else:
                    territory_id = f"GEN_{suffix}" if suffix else "GEN"
                
                # Confidence based on tier priority
                confidence = 90.0 - (tier_config.get("priority", 1) * 5)
                confidence = max(50.0, min(95.0, confidence))
                
                # Create result
                result = RuleResult(
                    territory_id=territory_id,
                    confidence=confidence,
                    rule_name=self.name,
                    metadata={
                        "tier": tier_name,
                        "tier_priority": tier_config.get("priority"),
                        "assignment_method": "tier_based"
                    }
                )
                
                logger.debug(
                    f"SegmentationRule assigned {territory_id} (tier: {tier_name})"
                )
                
                return result
        
        # No tier matched
        return RuleResult(
            territory_id=None,
            confidence=0.0,
            rule_name=self.name,
            metadata={"assignment_method": "no_tier_match"}
        )

