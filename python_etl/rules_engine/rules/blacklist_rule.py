"""
Blacklist Rule

Prevents specific client-territory assignments.
High priority rule that blocks certain combinations.
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional

from python_etl.rules_engine.base_rule import BaseRule, RuleResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlacklistRule(BaseRule):
    """
    Prevents specific client-territory assignments based on blacklist.
    
    Blacklist format (JSON):
    {
        "client_id_1": ["TERRITORY_A", "TERRITORY_B"],
        "client_id_2": ["TERRITORY_C"]
    }
    
    This rule has high priority (20) and prevents blacklisted assignments.
    Note: This rule returns None to indicate "no assignment", allowing
    other rules to potentially assign a different territory.
    """
    
    def __init__(
        self,
        blacklist_path: Optional[Path] = None,
        blacklist_dict: Optional[Dict[str, List[str]]] = None,
        priority: int = 20,
        enabled: bool = True
    ):
        """
        Initialize blacklist rule.
        
        Args:
            blacklist_path: Path to JSON file containing blacklist
            blacklist_dict: Dictionary of client_id -> [blocked_territory_ids]
            priority: Rule priority (default 20 - high)
            enabled: Whether rule is enabled (default True)
        """
        super().__init__(priority=priority, enabled=enabled)
        self.blacklist: Dict[str, Set[str]] = {}
        
        # Load blacklist from file or dict
        if blacklist_path:
            self.load_from_file(blacklist_path)
        elif blacklist_dict:
            # Convert lists to sets for faster lookup
            self.blacklist = {k: set(v) for k, v in blacklist_dict.items()}
        
        logger.info(f"BlacklistRule initialized with {len(self.blacklist)} entries")
    
    @property
    def name(self) -> str:
        """Return rule name."""
        return "BlacklistRule"
    
    def load_from_file(self, file_path: Path) -> None:
        """
        Load blacklist from JSON file.
        
        Args:
            file_path: Path to JSON file
        """
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Convert lists to sets
                    self.blacklist = {k: set(v) for k, v in data.items()}
                logger.info(f"Loaded {len(self.blacklist)} blacklist entries from {file_path}")
            else:
                logger.warning(f"Blacklist file not found: {file_path}")
                self.blacklist = {}
        except Exception as e:
            logger.error(f"Error loading blacklist: {e}")
            self.blacklist = {}
    
    def add_entry(self, client_id: str, territory_id: str) -> None:
        """
        Add a blacklist entry.
        
        Args:
            client_id: Client ID
            territory_id: Territory ID to block
        """
        client_id_str = str(client_id)
        if client_id_str not in self.blacklist:
            self.blacklist[client_id_str] = set()
        self.blacklist[client_id_str].add(territory_id)
        logger.debug(f"Added blacklist entry: {client_id} -X-> {territory_id}")
    
    def is_blocked(self, client_id: str, territory_id: str) -> bool:
        """
        Check if a client-territory combination is blacklisted.
        
        Args:
            client_id: Client ID
            territory_id: Territory ID
            
        Returns:
            True if combination is blacklisted
        """
        client_id_str = str(client_id)
        if client_id_str in self.blacklist:
            return territory_id in self.blacklist[client_id_str]
        return False
    
    def can_evaluate(self, client_record: pd.Series) -> bool:
        """
        Check if client has blacklist entries.
        
        Args:
            client_record: Client data
            
        Returns:
            True if client has blacklist entries
        """
        if not super().can_evaluate(client_record):
            return False
        
        # Check if client_id is in blacklist
        if "client_id" in client_record:
            client_id = str(client_record["client_id"])
            return client_id in self.blacklist
        
        return False
    
    def evaluate(self, client_record: pd.Series) -> RuleResult:
        """
        Evaluate blacklist rule for a client.
        
        Note: This rule doesn't assign territories, it only validates
        that proposed assignments are not blacklisted. In the current
        implementation, it returns None to indicate "skip this rule".
        
        A more sophisticated implementation would check the proposed
        territory and reject if blacklisted.
        
        Args:
            client_record: Client data
            
        Returns:
            RuleResult with None territory (indicating no assignment)
        """
        client_id = str(client_record["client_id"])
        blocked_territories = list(self.blacklist[client_id])
        
        # This rule doesn't make assignments, it only blocks them
        # Return None to let other rules handle assignment
        result = RuleResult(
            territory_id=None,
            confidence=0.0,
            rule_name=self.name,
            metadata={
                "client_id": client_id,
                "blocked_territories": blocked_territories,
                "assignment_method": "blacklist_check"
            }
        )
        
        logger.debug(
            f"BlacklistRule: Client {client_id} blocked from {len(blocked_territories)} territories"
        )
        
        return result

