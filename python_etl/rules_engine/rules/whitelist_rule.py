"""
Whitelist Rule

Explicit client-to-territory mappings that override all other rules.
Highest priority rule for manual territory assignments.
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, Optional

from python_etl.rules_engine.base_rule import BaseRule, RuleResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhitelistRule(BaseRule):
    """
    Assigns territories based on explicit whitelist mappings.
    
    Whitelist format (JSON):
    {
        "client_id_1": "TERRITORY_ID_1",
        "client_id_2": "TERRITORY_ID_2"
    }
    
    This rule has the highest priority (10) and overrides all other rules.
    """
    
    def __init__(
        self,
        whitelist_path: Optional[Path] = None,
        whitelist_dict: Optional[Dict[str, str]] = None,
        priority: int = 10,
        enabled: bool = True
    ):
        """
        Initialize whitelist rule.
        
        Args:
            whitelist_path: Path to JSON file containing whitelist
            whitelist_dict: Dictionary of client_id -> territory_id mappings
            priority: Rule priority (default 10 - highest)
            enabled: Whether rule is enabled (default True)
        """
        super().__init__(priority=priority, enabled=enabled)
        self.whitelist: Dict[str, str] = {}
        
        # Load whitelist from file or dict
        if whitelist_path:
            self.load_from_file(whitelist_path)
        elif whitelist_dict:
            self.whitelist = whitelist_dict
        
        logger.info(f"WhitelistRule initialized with {len(self.whitelist)} entries")
    
    @property
    def name(self) -> str:
        """Return rule name."""
        return "WhitelistRule"
    
    def load_from_file(self, file_path: Path) -> None:
        """
        Load whitelist from JSON file.
        
        Args:
            file_path: Path to JSON file
        """
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    self.whitelist = json.load(f)
                logger.info(f"Loaded {len(self.whitelist)} whitelist entries from {file_path}")
            else:
                logger.warning(f"Whitelist file not found: {file_path}")
                self.whitelist = {}
        except Exception as e:
            logger.error(f"Error loading whitelist: {e}")
            self.whitelist = {}
    
    def add_entry(self, client_id: str, territory_id: str) -> None:
        """
        Add a whitelist entry.
        
        Args:
            client_id: Client ID
            territory_id: Territory ID to assign
        """
        self.whitelist[str(client_id)] = territory_id
        logger.debug(f"Added whitelist entry: {client_id} -> {territory_id}")
    
    def remove_entry(self, client_id: str) -> bool:
        """
        Remove a whitelist entry.
        
        Args:
            client_id: Client ID to remove
            
        Returns:
            True if entry was removed, False if not found
        """
        client_id_str = str(client_id)
        if client_id_str in self.whitelist:
            del self.whitelist[client_id_str]
            logger.debug(f"Removed whitelist entry: {client_id}")
            return True
        return False
    
    def can_evaluate(self, client_record: pd.Series) -> bool:
        """
        Check if client is in whitelist.
        
        Args:
            client_record: Client data
            
        Returns:
            True if client is in whitelist
        """
        if not super().can_evaluate(client_record):
            return False
        
        # Check if client_id is in whitelist
        if "client_id" in client_record:
            client_id = str(client_record["client_id"])
            return client_id in self.whitelist
        
        return False
    
    def evaluate(self, client_record: pd.Series) -> RuleResult:
        """
        Evaluate whitelist rule for a client.
        
        Args:
            client_record: Client data
            
        Returns:
            RuleResult with whitelisted territory assignment
        """
        client_id = str(client_record["client_id"])
        territory_id = self.whitelist[client_id]
        
        # Whitelist assignments have maximum confidence
        confidence = 100.0
        
        # Create result
        result = RuleResult(
            territory_id=territory_id,
            confidence=confidence,
            rule_name=self.name,
            metadata={
                "client_id": client_id,
                "assignment_method": "whitelist",
                "override": True
            }
        )
        
        logger.debug(
            f"WhitelistRule assigned {territory_id} for client {client_id}"
        )
        
        return result


