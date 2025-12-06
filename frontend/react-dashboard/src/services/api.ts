/**
 * API Client Service
 * 
 * Handles all HTTP requests to the backend API.
 * Provides typed methods for each endpoint.
 */

import axios, { AxiosInstance } from 'axios'
import type {
  Territory,
  TerritoryDetail,
  Client,
  ClientDetail,
  ClientHierarchyNode,
  Advisor,
  AdvisorDetail,
  AdvisorStats,
  Assignment,
  AssignmentHistory,
  SystemStats,
  HealthCheck,
} from '../types'

// API base URL - uses Vite proxy in development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// =====================================================
// Territory API Methods
// =====================================================

export const territoryApi = {
  /**
   * Get all territories with optional filters
   */
  getAll: async (filters?: { region?: string; segment?: string }): Promise<Territory[]> => {
    const response = await apiClient.get<Territory[]>('/territories', { params: filters })
    return response.data
  },

  /**
   * Get territory by ID
   */
  getById: async (territoryId: string): Promise<TerritoryDetail> => {
    const response = await apiClient.get<TerritoryDetail>(`/territories/${territoryId}`)
    return response.data
  },

  /**
   * Get assignments for a territory
   */
  getAssignments: async (territoryId: string): Promise<Assignment[]> => {
    const response = await apiClient.get<Assignment[]>(`/territories/${territoryId}/assignments`)
    return response.data
  },
}

// =====================================================
// Client API Methods
// =====================================================

export const clientApi = {
  /**
   * Get all clients with optional filters
   */
  getAll: async (filters?: {
    region?: string
    segment?: string
    search?: string
    limit?: number
    offset?: number
  }): Promise<ClientDetail[]> => {
    const response = await apiClient.get<ClientDetail[]>('/clients', { params: filters })
    return response.data
  },

  /**
   * Get client by ID
   */
  getById: async (clientId: number): Promise<ClientDetail> => {
    const response = await apiClient.get<ClientDetail>(`/clients/${clientId}`)
    return response.data
  },

  /**
   * Get client hierarchy tree
   */
  getHierarchy: async (): Promise<ClientHierarchyNode[]> => {
    const response = await apiClient.get<ClientHierarchyNode[]>('/clients/hierarchy')
    return response.data
  },
}

// =====================================================
// Advisor API Methods
// =====================================================

export const advisorApi = {
  /**
   * Get all advisors with optional filters
   */
  getAll: async (filters?: { region?: string }): Promise<Advisor[]> => {
    const response = await apiClient.get<Advisor[]>('/advisors', { params: filters })
    return response.data
  },

  /**
   * Get advisor workload details
   */
  getWorkload: async (advisorEmail: string): Promise<AdvisorDetail> => {
    const response = await apiClient.get<AdvisorDetail>(`/advisors/${advisorEmail}/workload`)
    return response.data
  },

  /**
   * Get advisor statistics
   */
  getStats: async (): Promise<AdvisorStats> => {
    const response = await apiClient.get<AdvisorStats>('/advisors/stats')
    return response.data
  },
}

// =====================================================
// Assignment API Methods
// =====================================================

export const assignmentApi = {
  /**
   * Get all assignments with optional filters
   */
  getAll: async (filters?: {
    territory_id?: string
    advisor_email?: string
    limit?: number
  }): Promise<Assignment[]> => {
    const response = await apiClient.get<Assignment[]>('/assignments', { params: filters })
    return response.data
  },

  /**
   * Get assignment history
   */
  getHistory: async (clientId?: number, limit?: number): Promise<AssignmentHistory[]> => {
    const response = await apiClient.get<AssignmentHistory[]>('/assignments/history', {
      params: { client_id: clientId, limit },
    })
    return response.data
  },
}

// =====================================================
// System API Methods
// =====================================================

export const systemApi = {
  /**
   * Health check
   */
  health: async (): Promise<HealthCheck> => {
    const response = await apiClient.get<HealthCheck>('/health')
    return response.data
  },

  /**
   * Get system statistics
   */
  getStats: async (): Promise<SystemStats> => {
    const response = await apiClient.get<SystemStats>('/stats')
    return response.data
  },
}

// Export default API object
export default {
  territories: territoryApi,
  clients: clientApi,
  advisors: advisorApi,
  assignments: assignmentApi,
  system: systemApi,
}
