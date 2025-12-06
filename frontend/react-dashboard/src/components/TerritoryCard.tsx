/**
 * Territory Card Component
 * 
 * Displays territory summary with statistics
 */

import { MapPin, Users, UserCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import type { Territory } from '../types'

interface TerritoryCardProps {
  territory: Territory
  onClick?: () => void
}

export function TerritoryCard({ territory, onClick }: TerritoryCardProps) {
  return (
    <Card 
      className="cursor-pointer transition-all hover:shadow-md hover:scale-[1.02]"
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg">{territory.territory_id}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {territory.region} • {territory.segment}
            </p>
          </div>
          <Badge variant={territory.is_active ? "default" : "secondary"}>
            {territory.is_active ? "Active" : "Inactive"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {/* Client count */}
          <div className="flex items-center gap-2 text-sm">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">{territory.client_count}</span>
            <span className="text-muted-foreground">clients</span>
          </div>

          {/* Advisor count */}
          <div className="flex items-center gap-2 text-sm">
            <UserCircle className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">{territory.advisor_count}</span>
            <span className="text-muted-foreground">advisors</span>
          </div>

          {/* Owner role */}
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">{territory.owner_role}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
