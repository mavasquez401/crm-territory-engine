/**
 * Clients Page
 * 
 * Displays client hierarchy explorer with search and filters
 */

import { useEffect, useState } from 'react'
import { Search, Building2, Users } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { HierarchyTree } from '../components/HierarchyTree'
import { clientApi } from '../services/api'
import type { ClientHierarchyNode, Client, ClientDetail } from '../types'
import { formatNumber } from '../lib/utils'

export function Clients() {
  const [hierarchy, setHierarchy] = useState<ClientHierarchyNode[]>([])
  const [selectedClient, setSelectedClient] = useState<ClientDetail | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)

  // Load hierarchy on mount
  useEffect(() => {
    loadHierarchy()
  }, [])

  const loadHierarchy = async () => {
    try {
      setLoading(true)
      const data = await clientApi.getHierarchy()
      setHierarchy(data)
    } catch (error) {
      console.error('Error loading hierarchy:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadClientDetails = async (client: Client) => {
    try {
      const data = await clientApi.getById(client.client_key)
      setSelectedClient(data)
    } catch (error) {
      console.error('Error loading client details:', error)
    }
  }

  // Filter hierarchy by search query
  const filteredHierarchy = searchQuery
    ? hierarchy
        .map((node) => ({
          ...node,
          clients: node.clients.filter((client) =>
            client.client_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            client.parent_org.toLowerCase().includes(searchQuery.toLowerCase())
          ),
        }))
        .filter((node) => node.clients.length > 0)
    : hierarchy

  // Calculate statistics
  const totalOrgs = hierarchy.length
  const totalClients = hierarchy.reduce((sum, node) => sum + node.client_count, 0)

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Organizations</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalOrgs}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Clients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(totalClients)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Search Bar */}
      <Card>
        <CardHeader>
          <CardTitle>Client Hierarchy</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 mb-4">
            <Search className="h-5 w-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search clients or organizations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 rounded-md border px-3 py-2 text-sm"
            />
          </div>
        </CardContent>
      </Card>

      {/* Hierarchy Tree */}
      <HierarchyTree
        nodes={filteredHierarchy}
        onClientClick={loadClientDetails}
      />

      {filteredHierarchy.length === 0 && (
        <Card>
          <CardContent className="text-center py-12 text-muted-foreground">
            No clients found matching your search
          </CardContent>
        </Card>
      )}

      {/* Client Detail Modal */}
      {selectedClient && (
        <Card className="fixed inset-x-4 top-20 z-50 max-w-2xl mx-auto">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{selectedClient.client_name}</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Client ID: {selectedClient.client_key}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedClient(null)}
              >
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Client Details */}
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Region</p>
                  <p className="mt-1">{selectedClient.region}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Segment</p>
                  <p className="mt-1">{selectedClient.segment}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Parent Organization</p>
                  <p className="mt-1">{selectedClient.parent_org}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Primary Advisor</p>
                  <p className="mt-1 text-sm">{selectedClient.primary_advisor_email}</p>
                </div>
                {selectedClient.territory_id && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Territory</p>
                    <Badge className="mt-1">{selectedClient.territory_id}</Badge>
                  </div>
                )}
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Status</p>
                  <Badge variant={selectedClient.is_active ? "default" : "secondary"} className="mt-1">
                    {selectedClient.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
