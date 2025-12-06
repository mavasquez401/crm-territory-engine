"""
Pydantic Models for API Request/Response Validation

Defines data models for all API endpoints with validation.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# =====================================================
# Territory Models
# =====================================================

class Territory(BaseModel):
    """Territory information with statistics."""
    territory_id: str = Field(..., description="Territory identifier (e.g., NOR_INS)")
    region: str = Field(..., description="Geographic region")
    segment: str = Field(..., description="Client segment")
    owner_role: str = Field(default="Sales Rep", description="Territory owner role")
    client_count: int = Field(default=0, description="Number of clients in territory")
    advisor_count: int = Field(default=0, description="Number of advisors in territory")
    is_active: bool = Field(default=True, description="Whether territory is active")


class TerritoryDetail(Territory):
    """Detailed territory information with assignments."""
    description: Optional[str] = Field(None, description="Territory description")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


# =====================================================
# Client Models
# =====================================================

class Client(BaseModel):
    """Client information."""
    client_key: int = Field(..., description="Unique client identifier")
    client_name: str = Field(..., description="Client name")
    region: str = Field(..., description="Geographic region")
    segment: str = Field(..., description="Client segment")
    parent_org: str = Field(..., description="Parent organization")
    primary_advisor_email: EmailStr = Field(..., description="Primary advisor email")
    is_active: bool = Field(default=True, description="Whether client is active")


class ClientDetail(Client):
    """Detailed client information with assignment."""
    territory_id: Optional[str] = Field(None, description="Assigned territory")
    assignment_type: Optional[str] = Field(None, description="Assignment type")
    effective_date: Optional[str] = Field(None, description="Assignment effective date")


class ClientHierarchyNode(BaseModel):
    """Client hierarchy tree node."""
    parent_org: str = Field(..., description="Parent organization name")
    clients: List[Client] = Field(default_factory=list, description="Clients in organization")
    client_count: int = Field(..., description="Total clients in organization")


# =====================================================
# Advisor Models
# =====================================================

class Advisor(BaseModel):
    """Advisor information with workload metrics."""
    advisor_email: EmailStr = Field(..., description="Advisor email address")
    client_count: int = Field(default=0, description="Number of clients")
    territory_count: int = Field(default=0, description="Number of territories")
    regions: List[str] = Field(default_factory=list, description="Regions covered")


class AdvisorDetail(Advisor):
    """Detailed advisor information."""
    clients: List[Client] = Field(default_factory=list, description="List of clients")
    territories: List[str] = Field(default_factory=list, description="Territory IDs")


class AdvisorStats(BaseModel):
    """Overall advisor statistics."""
    total_advisors: int = Field(..., description="Total number of advisors")
    avg_clients_per_advisor: float = Field(..., description="Average clients per advisor")
    max_clients: int = Field(..., description="Maximum clients for any advisor")
    min_clients: int = Field(..., description="Minimum clients for any advisor")


# =====================================================
# Assignment Models
# =====================================================

class Assignment(BaseModel):
    """Client-territory assignment."""
    client_key: int = Field(..., description="Client identifier")
    client_name: str = Field(..., description="Client name")
    territory_id: str = Field(..., description="Territory identifier")
    primary_advisor_email: EmailStr = Field(..., description="Primary advisor")
    assignment_type: str = Field(default="PRIMARY", description="Assignment type")
    is_current: bool = Field(default=True, description="Whether assignment is current")


class AssignmentHistory(Assignment):
    """Assignment with history information."""
    effective_date: Optional[str] = Field(None, description="Effective date")
    end_date: Optional[str] = Field(None, description="End date")
    assigned_by_rule: Optional[str] = Field(None, description="Rule that made assignment")
    confidence_score: Optional[float] = Field(None, description="Assignment confidence")


# =====================================================
# System Models
# =====================================================

class HealthCheck(BaseModel):
    """API health check response."""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")


class SystemStats(BaseModel):
    """Overall system statistics."""
    total_clients: int = Field(..., description="Total number of clients")
    total_territories: int = Field(..., description="Total number of territories")
    total_advisors: int = Field(..., description="Total number of advisors")
    total_assignments: int = Field(..., description="Total current assignments")
    avg_clients_per_territory: float = Field(..., description="Average clients per territory")
    data_last_updated: Optional[str] = Field(None, description="Last data update timestamp")


# =====================================================
# Response Models
# =====================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    items: List = Field(..., description="List of items")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(..., description="Error timestamp")
