/**
 * Advisor Card Component
 * 
 * Displays advisor summary with workload metrics
 */

import { UserCircle, Users, MapPin, Briefcase } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import type { Advisor } from '../types'

interface AdvisorCardProps {
  advisor: Advisor
  onClick?: () => void
}

export function AdvisorCard({ advisor, onClick }: AdvisorCardProps) {
  // Calculate workload level (simple heuristic)
  const getWorkloadLevel = (clientCount: number) => {
    if (clientCount >= 50) return { label: 'High', variant: 'destructive' as const }
    if (clientCount >= 20) return { label: 'Medium', variant: 'default' as const }
    return { label: 'Low', variant: 'secondary' as const }
  }

  const workload = getWorkloadLevel(advisor.client_count)

  return (
    <Card 
      className="cursor-pointer transition-all hover:shadow-md hover:scale-[1.02]"
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-primary/10 p-2">
              <UserCircle className="h-6 w-6 text-primary" />
            </div>
            <div>
              <CardTitle className="text-base">{advisor.advisor_email}</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                {advisor.regions.join(', ')}
              </p>
            </div>
          </div>
          <Badge variant={workload.variant}>{workload.label}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {/* Client count */}
          <div className="flex items-center gap-2 text-sm">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">{advisor.client_count}</span>
            <span className="text-muted-foreground">clients</span>
          </div>

          {/* Territory count */}
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">{advisor.territory_count}</span>
            <span className="text-muted-foreground">
              {advisor.territory_count === 1 ? 'territory' : 'territories'}
            </span>
          </div>

          {/* Workload bar */}
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-muted-foreground">Workload</span>
              <span className="font-medium">{advisor.client_count}/100</span>
            </div>
            <div className="h-2 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${Math.min((advisor.client_count / 100) * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
