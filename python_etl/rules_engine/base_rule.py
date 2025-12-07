"""
Base Rule Module

Defines abstract base class for all territory assignment rules.
All rules must extend BaseRule and implement the evaluate() method.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
import pandas as pd


@dataclass
class RuleResult:
    """
    Result of a rule evaluation.
    
    Attributes:
        territory_id: Assigned territory ID (None if no assignment)
        confidence: Confidence score (0-100)
        rule_name: Name of rule that made the assignment
        metadata: Additional information about the assignment
    """
    territory_id: Optional[str]
    confidence: float
    rule_name: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseRule(ABC):
    """
    Abstract base class for territory assignment rules.
    
    All rules must implement:
    - evaluate(): Evaluate rule for a client record
    - priority: Priority level (lower number = higher priority)
    - name: Rule name for logging and tracking
    """
    
    def __init__(self, priority: int = 100, enabled: bool = True):
        """
        Initialize base rule.
        
        Args:
            priority: Rule priority (lower = higher priority, default 100)
            enabled: Whether rule is enabled (default True)
        """
        self.priority = priority
        self.enabled = enabled
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this rule."""
        pass
    
    @abstractmethod
    def evaluate(self, client_record: pd.Series) -> RuleResult:
        """
        Evaluate rule for a single client record.
        
        Args:
            client_record: Pandas Series containing client data
            
        Returns:
            RuleResult with territory assignment or None
        """
        pass
    
    def can_evaluate(self, client_record: pd.Series) -> bool:
        """
        Check if this rule can evaluate the given client record.
        
        Args:
            client_record: Pandas Series containing client data
            
        Returns:
            True if rule can evaluate this record
        """
        return self.enabled
    
    def __repr__(self) -> str:
        """String representation of rule."""
        return f"{self.name} (priority={self.priority}, enabled={self.enabled})"
    
    def __lt__(self, other: 'BaseRule') -> bool:
        """
        Compare rules by priority for sorting.
        Lower priority number = higher priority = evaluated first.
        """
        return self.priority < other.priority


