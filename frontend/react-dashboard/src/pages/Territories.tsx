/**
 * Territories Page
 * 
 * Displays all territories with filtering and statistics
 */

import { useEffect, useState } from 'react'
import { MapPin, Filter, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { TerritoryCard } from '../components/TerritoryCard'
import { territoryApi, assignmentApi } from '../services/api'
import type { Territory, Assignment } from '../types'
import { formatNumber } from '../lib/utils'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'

// Colors for charts
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export function Territories() {
  const [territories, setTerritories] = useState<Territory[]>([])
  const [selectedTerritory, setSelectedTerritory] = useState<Territory | null>(null)
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [loading, setLoading] = useState(true)
  const [filterRegion, setFilterRegion] = useState<string>('')
  const [filterSegment, setFilterSegment] = useState<string>('')

  // Load territories on mount
  useEffect(() => {
    loadTerritories()
  }, [filterRegion, filterSegment])

  const loadTerritories = async () => {
    try {
      setLoading(true)
      const filters: any = {}
      if (filterRegion) filters.region = filterRegion
      if (filterSegment) filters.segment = filterSegment
      
      const data = await territoryApi.getAll(filters)
      setTerritories(data)
    } catch (error) {
      console.error('Error loading territories:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTerritoryAssignments = async (territoryId: string) => {
    try {
      const data = await territoryApi.getAssignments(territoryId)
      setAssignments(data)
    } catch (error) {
      console.error('Error loading assignments:', error)
    }
  }

  const handleTerritoryClick = (territory: Territory) => {
    setSelectedTerritory(territory)
    loadTerritoryAssignments(territory.territory_id)
  }

  // Calculate statistics
  const totalClients = territories.reduce((sum, t) => sum + t.client_count, 0)
  const totalAdvisors = territories.reduce((sum, t) => sum + t.advisor_count, 0)
  const avgClientsPerTerritory = territories.length > 0 ? totalClients / territories.length : 0

  // Get unique regions and segments for filters
  const regions = Array.from(new Set(territories.map(t => t.region)))
  const segments = Array.from(new Set(territories.map(t => t.segment)))

  // Prepare chart data
  const regionData = territories.reduce((acc: any[], territory) => {
    const existing = acc.find(item => item.name === territory.region)
    if (existing) {
      existing.value += territory.client_count
    } else {
      acc.push({ name: territory.region, value: territory.client_count })
    }
    return acc
  }, [])

  const barChartData = territories.map(t => ({
    name: t.territory_id,
    clients: t.client_count,
    advisors: t.advisor_count
  }))

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Territories</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{territories.length}</div>
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

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Clients/Territory</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgClientsPerTerritory.toFixed(1)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Pie Chart - Territory Distribution by Region */}
        <Card>
          <CardHeader>
            <CardTitle>Territory Distribution by Region</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={regionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => entry.name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {regionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Bar Chart - Clients per Territory */}
        <Card>
          <CardHeader>
            <CardTitle>Clients per Territory</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="clients" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Territories</CardTitle>
            <div className="flex gap-2">
              <Filter className="h-5 w-5 text-muted-foreground" />
              <select
                value={filterRegion}
                onChange={(e) => setFilterRegion(e.target.value)}
                className="rounded-md border px-3 py-1 text-sm"
              >
                <option value="">All Regions</option>
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
              <select
                value={filterSegment}
                onChange={(e) => setFilterSegment(e.target.value)}
                className="rounded-md border px-3 py-1 text-sm"
              >
                <option value="">All Segments</option>
                {segments.map(segment => (
                  <option key={segment} value={segment}>{segment}</option>
                ))}
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Territory Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {territories.map((territory) => (
              <TerritoryCard
                key={territory.territory_id}
                territory={territory}
                onClick={() => handleTerritoryClick(territory)}
              />
            ))}
          </div>

          {territories.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              No territories found
            </div>
          )}
        </CardContent>
      </Card>

      {/* Territory Detail Modal (Simple version) */}
      {selectedTerritory && (
        <Card className="fixed inset-x-4 top-20 z-50 max-w-2xl mx-auto max-h-[80vh] overflow-auto">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{selectedTerritory.territory_id}</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {selectedTerritory.region} • {selectedTerritory.segment}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedTerritory(null)}
              >
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Assignments ({assignments.length})</h4>
                <div className="space-y-2">
                  {assignments.map((assignment) => (
                    <div
                      key={assignment.client_key}
                      className="flex items-center justify-between p-3 border rounded-md"
                    >
                      <div>
                        <p className="font-medium">{assignment.client_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {assignment.primary_advisor_email}
                        </p>
                      </div>
                      <Badge>{assignment.assignment_type}</Badge>
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
