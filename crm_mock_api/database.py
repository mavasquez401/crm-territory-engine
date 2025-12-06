"""
Database Access Layer

Reads data from CSV files (or Snowflake if configured).
Provides data access methods for all API endpoints.
"""

import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CORE_DIR = DATA_DIR / "core"
REPORTS_DIR = DATA_DIR / "reports"


class Database:
    """
    Data access layer for CRM data.
    
    Reads from CSV files by default, can be extended to use Snowflake.
    """
    
    def __init__(self):
        """Initialize database connection."""
        self.client_dim_path = CORE_DIR / "client_dim.csv"
        self.territory_dim_path = CORE_DIR / "territory_dim.csv"
        self.assignments_fact_path = CORE_DIR / "assignments_fact.csv"
        self.assignment_changes_path = REPORTS_DIR / "assignment_changes.csv"
        
        # Cache for data
        self._clients_cache = None
        self._territories_cache = None
        self._assignments_cache = None
        self._last_load_time = None
    
    def _should_reload(self) -> bool:
        """Check if data should be reloaded (cache invalidation)."""
        if self._last_load_time is None:
            return True
        # Reload if cache is older than 5 minutes
        elapsed = (datetime.now() - self._last_load_time).total_seconds()
        return elapsed > 300
    
    def _load_data(self) -> None:
        """Load all data from CSV files."""
        logger.info("Loading data from CSV files")
        
        try:
            self._clients_cache = pd.read_csv(self.client_dim_path)
            self._territories_cache = pd.read_csv(self.territory_dim_path)
            self._assignments_cache = pd.read_csv(self.assignments_fact_path)
            self._last_load_time = datetime.now()
            
            logger.info(f"Loaded {len(self._clients_cache)} clients, "
                       f"{len(self._territories_cache)} territories, "
                       f"{len(self._assignments_cache)} assignments")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def get_clients(self) -> pd.DataFrame:
        """Get all clients."""
        if self._should_reload():
            self._load_data()
        return self._clients_cache.copy()
    
    def get_territories(self) -> pd.DataFrame:
        """Get all territories."""
        if self._should_reload():
            self._load_data()
        return self._territories_cache.copy()
    
    def get_assignments(self) -> pd.DataFrame:
        """Get all current assignments."""
        if self._should_reload():
            self._load_data()
        # Filter for current assignments only
        return self._assignments_cache[
            self._assignments_cache['is_current'] == True
        ].copy()
    
    def get_client_by_id(self, client_id: int) -> Optional[Dict[str, Any]]:
        """Get client by ID."""
        clients = self.get_clients()
        client = clients[clients['client_key'] == client_id]
        
        if client.empty:
            return None
        
        return client.iloc[0].to_dict()
    
    def get_territory_by_id(self, territory_id: str) -> Optional[Dict[str, Any]]:
        """Get territory by ID."""
        territories = self.get_territories()
        territory = territories[territories['territory_id'] == territory_id]
        
        if territory.empty:
            return None
        
        return territory.iloc[0].to_dict()
    
    def get_assignments_by_territory(self, territory_id: str) -> pd.DataFrame:
        """Get all assignments for a territory."""
        assignments = self.get_assignments()
        return assignments[assignments['territory_id'] == territory_id].copy()
    
    def get_assignments_by_advisor(self, advisor_email: str) -> pd.DataFrame:
        """Get all assignments for an advisor."""
        assignments = self.get_assignments()
        return assignments[
            assignments['primary_advisor_email'] == advisor_email
        ].copy()
    
    def get_client_hierarchy(self) -> List[Dict[str, Any]]:
        """Get client hierarchy grouped by parent organization."""
        clients = self.get_clients()
        
        # Group by parent_org
        hierarchy = []
        for parent_org, group in clients.groupby('parent_org'):
            hierarchy.append({
                'parent_org': parent_org,
                'clients': group.to_dict('records'),
                'client_count': len(group)
            })
        
        return hierarchy
    
    def get_advisor_list(self) -> List[str]:
        """Get list of unique advisors."""
        assignments = self.get_assignments()
        return sorted(assignments['primary_advisor_email'].unique().tolist())
    
    def get_assignment_history(self) -> pd.DataFrame:
        """Get assignment change history."""
        try:
            if self.assignment_changes_path.exists():
                return pd.read_csv(self.assignment_changes_path)
            else:
                logger.warning("Assignment history file not found")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading assignment history: {e}")
            return pd.DataFrame()
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        clients = self.get_clients()
        territories = self.get_territories()
        assignments = self.get_assignments()
        advisors = self.get_advisor_list()
        
        stats = {
            'total_clients': len(clients),
            'total_territories': len(territories),
            'total_advisors': len(advisors),
            'total_assignments': len(assignments),
            'avg_clients_per_territory': len(clients) / len(territories) if len(territories) > 0 else 0,
            'data_last_updated': self._last_load_time.isoformat() if self._last_load_time else None
        }
        
        return stats


# Global database instance
db = Database()
