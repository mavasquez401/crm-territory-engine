/**
 * Advisors Page
 * 
 * Displays advisor workloads with metrics and filtering
 */

import { useEffect, useState } from 'react'
import { UserCircle, TrendingUp, TrendingDown, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { AdvisorCard } from '../components/AdvisorCard'
import { advisorApi } from '../services/api'
import type { Advisor, AdvisorDetail, AdvisorStats } from '../types'
import { formatNumber } from '../lib/utils'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export function Advisors() {
  const [advisors, setAdvisors] = useState<Advisor[]>([])
  const [stats, setStats] = useState<AdvisorStats | null>(null)
  const [selectedAdvisor, setSelectedAdvisor] = useState<AdvisorDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState<'clients' | 'territories'>('clients')

  // Load advisors on mount
  useEffect(() => {
    loadAdvisors()
    loadStats()
  }, [])

  const loadAdvisors = async () => {
    try {
      setLoading(true)
      const data = await advisorApi.getAll()
      setAdvisors(data)
    } catch (error) {
      console.error('Error loading advisors:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const data = await advisorApi.getStats()
      setStats(data)
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const loadAdvisorDetails = async (advisorEmail: string) => {
    try {
      const data = await advisorApi.getWorkload(advisorEmail)
      setSelectedAdvisor(data)
    } catch (error) {
      console.error('Error loading advisor details:', error)
    }
  }

  // Sort advisors
  const sortedAdvisors = [...advisors].sort((a, b) => {
    if (sortBy === 'clients') {
      return b.client_count - a.client_count
    }
    return b.territory_count - a.territory_count
  })

  // Prepare chart data (top 10 advisors)
  const chartData = sortedAdvisors.slice(0, 10).map(advisor => ({
    name: advisor.advisor_email.split('@')[0], // Just the name part
    clients: advisor.client_count,
    territories: advisor.territory_count
  }))

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Advisors</CardTitle>
              <UserCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_advisors}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Clients/Advisor</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.avg_clients_per_advisor.toFixed(1)}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Highest Workload</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.max_clients}</div>
              <p className="text-xs text-muted-foreground mt-1">clients</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Lowest Workload</CardTitle>
              <TrendingDown className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.min_clients}</div>
              <p className="text-xs text-muted-foreground mt-1">clients</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Workload Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Top 10 Advisors by Workload</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="clients" fill="#3b82f6" name="Clients" />
              <Bar dataKey="territories" fill="#10b981" name="Territories" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Advisor List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Advisors</CardTitle>
            <div className="flex gap-2">
              <Button
                variant={sortBy === 'clients' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSortBy('clients')}
              >
                Sort by Clients
              </Button>
              <Button
                variant={sortBy === 'territories' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSortBy('territories')}
              >
                Sort by Territories
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {sortedAdvisors.map((advisor) => (
              <AdvisorCard
                key={advisor.advisor_email}
                advisor={advisor}
                onClick={() => loadAdvisorDetails(advisor.advisor_email)}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Advisor Detail Modal */}
      {selectedAdvisor && (
        <Card className="fixed inset-x-4 top-20 z-50 max-w-3xl mx-auto max-h-[80vh] overflow-auto">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{selectedAdvisor.advisor_email}</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {selectedAdvisor.client_count} clients across {selectedAdvisor.territory_count} territories
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedAdvisor(null)}
              >
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Territories */}
              <div>
                <h4 className="font-semibold mb-2">Territories</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedAdvisor.territories.map((territory) => (
                    <Badge key={territory} variant="outline">
                      {territory}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Clients */}
              <div>
                <h4 className="font-semibold mb-2">Clients ({selectedAdvisor.clients.length})</h4>
                <div className="space-y-2 max-h-96 overflow-auto">
                  {selectedAdvisor.clients.map((client) => (
                    <div
                      key={client.client_key}
                      className="flex items-center justify-between p-3 border rounded-md"
                    >
                      <div>
                        <p className="font-medium">{client.client_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {client.region} • {client.segment}
                        </p>
                      </div>
                      <Badge variant="outline">{client.parent_org}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
