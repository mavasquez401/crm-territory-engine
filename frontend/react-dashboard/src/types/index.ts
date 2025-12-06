/**
 * TypeScript type definitions for the application
 */

// Territory types
export interface Territory {
  territory_id: string
  region: string
  segment: string
  owner_role: string
  client_count: number
  advisor_count: number
  is_active: boolean
}

export interface TerritoryDetail extends Territory {
  description?: string
  created_at?: string
  updated_at?: string
}

// Client types
export interface Client {
  client_key: number
  client_name: string
  region: string
  segment: string
  parent_org: string
  primary_advisor_email: string
  is_active: boolean
}

export interface ClientDetail extends Client {
  territory_id?: string
  assignment_type?: string
  effective_date?: string
}

export interface ClientHierarchyNode {
  parent_org: string
  clients: Client[]
  client_count: number
}

// Advisor types
export interface Advisor {
  advisor_email: string
  client_count: number
  territory_count: number
  regions: string[]
}

export interface AdvisorDetail extends Advisor {
  clients: Client[]
  territories: string[]
}

export interface AdvisorStats {
  total_advisors: number
  avg_clients_per_advisor: number
  max_clients: number
  min_clients: number
}

// Assignment types
export interface Assignment {
  client_key: number
  client_name: string
  territory_id: string
  primary_advisor_email: string
  assignment_type: string
  is_current: boolean
}

export interface AssignmentHistory extends Assignment {
  effective_date?: string
  end_date?: string
  assigned_by_rule?: string
  confidence_score?: number
}

// System types
export interface SystemStats {
  total_clients: number
  total_territories: number
  total_advisors: number
  total_assignments: number
  avg_clients_per_territory: number
  data_last_updated?: string
}

export interface HealthCheck {
  status: string
  timestamp: string
  version: string
}
