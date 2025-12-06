"""
Territory Assigner Module

Orchestrates rule evaluation for territory assignment.
Manages multiple rules, evaluates them in priority order, and resolves conflicts.
"""

from typing import List, Optional, Dict, Any
import pandas as pd
import logging

from python_etl.rules_engine.base_rule import BaseRule, RuleResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TerritoryAssigner:
    """
    Orchestrates territory assignment using multiple rules.
    
    Rules are evaluated in priority order (lowest priority number first).
    First rule to return a confident assignment wins.
    """
    
    def __init__(self):
        """Initialize territory assigner with empty rule list."""
        self.rules: List[BaseRule] = []
    
    def add_rule(self, rule: BaseRule) -> None:
        """
        Add a rule to the assigner.
        
        Args:
            rule: Rule to add
        """
        self.rules.append(rule)
        # Sort rules by priority (lower number = higher priority)
        self.rules.sort()
        logger.info(f"Added rule: {rule.name} (priority={rule.priority})")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a rule by name.
        
        Args:
            rule_name: Name of rule to remove
            
        Returns:
            True if rule was removed, False if not found
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                logger.info(f"Removed rule: {rule_name}")
                return True
        logger.warning(f"Rule not found: {rule_name}")
        return False
    
    def get_rules(self) -> List[BaseRule]:
        """
        Get list of all rules sorted by priority.
        
        Returns:
            List of rules
        """
        return sorted(self.rules)
    
    def assign_territory(
        self,
        client_record: pd.Series,
        min_confidence: float = 0.0
    ) -> Optional[RuleResult]:
        """
        Assign territory to a client using registered rules.
        
        Rules are evaluated in priority order. First rule to return
        a confident assignment (above min_confidence) wins.
        
        Args:
            client_record: Client data as Pandas Series
            min_confidence: Minimum confidence threshold (0-100)
            
        Returns:
            RuleResult with assignment, or None if no rule matched
        """
        # Evaluate rules in priority order
        for rule in self.get_rules():
            # Skip disabled rules
            if not rule.enabled:
                continue
            
            # Check if rule can evaluate this record
            if not rule.can_evaluate(client_record):
                continue
            
            # Evaluate rule
            try:
                result = rule.evaluate(client_record)
                
                # Check if rule returned an assignment
                if result and result.territory_id:
                    # Check confidence threshold
                    if result.confidence >= min_confidence:
                        logger.debug(
                            f"Rule '{rule.name}' assigned territory '{result.territory_id}' "
                            f"with confidence {result.confidence}%"
                        )
                        return result
                    
            except Exception as e:
                logger.error(f"Error evaluating rule '{rule.name}': {e}")
                continue
        
        # No rule matched
        logger.warning(
            f"No rule matched for client {client_record.get('client_id', 'Unknown')}"
        )
        return None
    
    def assign_territories_bulk(
        self,
        clients_df: pd.DataFrame,
        min_confidence: float = 0.0
    ) -> pd.DataFrame:
        """
        Assign territories to multiple clients.
        
        Args:
            clients_df: DataFrame containing client records
            min_confidence: Minimum confidence threshold
            
        Returns:
            DataFrame with territory assignments added
        """
        logger.info(f"Assigning territories to {len(clients_df)} clients")
        
        # Initialize result columns
        clients_df = clients_df.copy()
        clients_df["assigned_territory_id"] = None
        clients_df["assignment_confidence"] = 0.0
        clients_df["assignment_rule"] = None
        
        # Assign territory for each client
        for idx, row in clients_df.iterrows():
            result = self.assign_territory(row, min_confidence)
            
            if result:
                clients_df.at[idx, "assigned_territory_id"] = result.territory_id
                clients_df.at[idx, "assignment_confidence"] = result.confidence
                clients_df.at[idx, "assignment_rule"] = result.rule_name
        
        # Log summary
        assigned_count = clients_df["assigned_territory_id"].notna().sum()
        logger.info(f"Successfully assigned {assigned_count}/{len(clients_df)} clients")
        
        return clients_df
    
    def resolve_conflicts(
        self,
        assignments: List[RuleResult]
    ) -> Optional[RuleResult]:
        """
        Resolve conflicts when multiple rules assign different territories.
        
        Currently uses simple priority-based resolution:
        - Highest confidence wins
        - If tied, lowest priority number (highest priority) wins
        
        Args:
            assignments: List of RuleResults from different rules
            
        Returns:
            Winning RuleResult, or None if no valid assignments
        """
        if not assignments:
            return None
        
        # Filter out None assignments
        valid_assignments = [a for a in assignments if a and a.territory_id]
        
        if not valid_assignments:
            return None
        
        # Sort by confidence (descending), then priority (ascending)
        # This is a simplified conflict resolution strategy
        sorted_assignments = sorted(
            valid_assignments,
            key=lambda x: (-x.confidence, x.rule_name),
            reverse=False
        )
        
        winner = sorted_assignments[0]
        
        if len(valid_assignments) > 1:
            logger.warning(
                f"Conflict resolved: {len(valid_assignments)} rules matched, "
                f"chose '{winner.rule_name}' (confidence={winner.confidence}%)"
            )
        
        return winner
    
    def get_rule_statistics(self, assignments_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistics about rule usage in assignments.
        
        Args:
            assignments_df: DataFrame with assignment_rule column
            
        Returns:
            Dictionary with rule statistics
        """
        if "assignment_rule" not in assignments_df.columns:
            return {}
        
        rule_counts = assignments_df["assignment_rule"].value_counts().to_dict()
        total_assigned = assignments_df["assignment_rule"].notna().sum()
        
        stats = {
            "total_clients": len(assignments_df),
            "total_assigned": total_assigned,
            "unassigned": len(assignments_df) - total_assigned,
            "rule_usage": rule_counts,
            "assignment_rate": (total_assigned / len(assignments_df) * 100) if len(assignments_df) > 0 else 0
        }
        
        logger.info(f"Rule Statistics:")
        logger.info(f"  Total clients: {stats['total_clients']}")
        logger.info(f"  Assigned: {stats['total_assigned']} ({stats['assignment_rate']:.1f}%)")
        logger.info(f"  Rule usage: {rule_counts}")
        
        return stats

