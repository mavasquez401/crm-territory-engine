/**
 * Hierarchy Tree Component
 * 
 * Displays client organizational hierarchy in tree structure
 */

import { useState } from 'react'
import { ChevronDown, ChevronRight, Building2, User, MapPin } from 'lucide-react'
import { Badge } from './ui/badge'
import { Card, CardContent } from './ui/card'
import type { ClientHierarchyNode, Client } from '../types'

interface HierarchyTreeProps {
  nodes: ClientHierarchyNode[]
  onClientClick?: (client: Client) => void
}

export function HierarchyTree({ nodes, onClientClick }: HierarchyTreeProps) {
  const [expandedOrgs, setExpandedOrgs] = useState<Set<string>>(new Set())

  const toggleOrg = (orgName: string) => {
    const newExpanded = new Set(expandedOrgs)
    if (newExpanded.has(orgName)) {
      newExpanded.delete(orgName)
    } else {
      newExpanded.add(orgName)
    }
    setExpandedOrgs(newExpanded)
  }

  // Get segment color
  const getSegmentColor = (segment: string) => {
    if (segment === 'Institutional') return 'bg-blue-100 text-blue-800'
    if (segment === 'Retail') return 'bg-green-100 text-green-800'
    return 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-2">
      {nodes.map((node) => {
        const isExpanded = expandedOrgs.has(node.parent_org)

        return (
          <Card key={node.parent_org} className="overflow-hidden">
            {/* Organization Header */}
            <div
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-accent transition-colors"
              onClick={() => toggleOrg(node.parent_org)}
            >
              <div className="flex items-center gap-3">
                {isExpanded ? (
                  <ChevronDown className="h-5 w-5 text-muted-foreground" />
                ) : (
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
                )}
                <Building2 className="h-5 w-5 text-primary" />
                <div>
                  <h3 className="font-semibold">{node.parent_org}</h3>
                  <p className="text-sm text-muted-foreground">
                    {node.client_count} {node.client_count === 1 ? 'client' : 'clients'}
                  </p>
                </div>
              </div>
              <Badge variant="secondary">{node.client_count}</Badge>
            </div>

            {/* Clients List (when expanded) */}
            {isExpanded && (
              <CardContent className="pt-0">
                <div className="space-y-2 pl-8">
                  {node.clients.map((client) => (
                    <div
                      key={client.client_key}
                      className="flex items-center justify-between p-3 border rounded-md hover:bg-accent cursor-pointer transition-colors"
                      onClick={() => onClientClick?.(client)}
                    >
                      <div className="flex items-center gap-3">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{client.client_name}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <MapPin className="h-3 w-3 text-muted-foreground" />
                            <p className="text-xs text-muted-foreground">
                              {client.region}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant="outline"
                          className={getSegmentColor(client.segment)}
                        >
                          {client.segment}
                        </Badge>
                        {client.is_active && (
                          <Badge variant="default">Active</Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            )}
          </Card>
        )
      })}
    </div>
  )
}
