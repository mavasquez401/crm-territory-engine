/**
 * Dashboard Home Page
 * 
 * Overview dashboard with key metrics and quick links
 */

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MapPin, Users, UserCircle, TrendingUp, ArrowRight, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { systemApi, assignmentApi } from '../services/api'
import type { SystemStats, AssignmentHistory } from '../types'
import { formatNumber } from '../lib/utils'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

// Colors for charts
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']

export function Dashboard() {
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [recentChanges, setRecentChanges] = useState<AssignmentHistory[]>([])
  const [loading, setLoading] = useState(true)

  // Load data on mount
  useEffect(() => {
    loadStats()
    loadRecentChanges()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const data = await systemApi.getStats()
      setStats(data)
    } catch (error) {
      console.error('Error loading stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadRecentChanges = async () => {
    try {
      const data = await assignmentApi.getHistory(undefined, 10)
      setRecentChanges(data)
    } catch (error) {
      console.error('Error loading recent changes:', error)
    }
  }

  if (loading || !stats) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  // Prepare chart data
  const distributionData = [
    { name: 'Clients', value: stats.total_clients },
    { name: 'Territories', value: stats.total_territories },
    { name: 'Advisors', value: stats.total_advisors },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold">CRM Territory Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Enterprise territory management and client segmentation system
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Clients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.total_clients)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Active client accounts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Territories</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_territories}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Active territories
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Advisors</CardTitle>
            <UserCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_advisors}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Managing clients
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Clients/Territory</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.avg_clients_per_territory.toFixed(1)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Distribution metric
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* System Overview Chart */}
        <Card>
          <CardHeader>
            <CardTitle>System Overview</CardTitle>
            <CardDescription>Distribution of entities</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent Assignment Changes */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Assignment Changes</CardTitle>
            <CardDescription>Latest territory assignments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentChanges.length > 0 ? (
                recentChanges.slice(0, 5).map((change, index) => (
                  <div key={index} className="flex items-center justify-between p-2 border-b last:border-0">
                    <div className="flex-1">
                      <p className="text-sm font-medium">{change.client_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {change.territory_id}
                      </p>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {change.assigned_by_rule || 'System'}
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No recent changes
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Links */}
      <div className="grid gap-4 md:grid-cols-3">
        <Link to="/territories">
          <Card className="cursor-pointer transition-all hover:shadow-md hover:scale-[1.02]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                View Territories
              </CardTitle>
              <CardDescription>
                Explore territory assignments and distribution
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="ghost" className="w-full justify-between">
                Go to Territories
                <ArrowRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </Link>

        <Link to="/clients">
          <Card className="cursor-pointer transition-all hover:shadow-md hover:scale-[1.02]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Client Hierarchy
              </CardTitle>
              <CardDescription>
                Browse client organizational structure
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="ghost" className="w-full justify-between">
                Go to Clients
                <ArrowRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </Link>

        <Link to="/advisors">
          <Card className="cursor-pointer transition-all hover:shadow-md hover:scale-[1.02]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserCircle className="h-5 w-5" />
                Advisor Workloads
              </CardTitle>
              <CardDescription>
                Monitor advisor capacity and assignments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="ghost" className="w-full justify-between">
                Go to Advisors
                <ArrowRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* System Health */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            System Health
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">All systems operational</p>
              {stats.data_last_updated && (
                <p className="text-xs text-muted-foreground mt-1">
                  Last updated: {new Date(stats.data_last_updated).toLocaleString()}
                </p>
              )}
            </div>
            <Badge variant="default" className="bg-green-500">
              Healthy
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
