/**
 * Client Card Component
 * 
 * Displays client information with territory assignment.
 */

import { Building2, MapPin, User, Mail } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import type { ClientWithTerritory } from '../types';

interface ClientCardProps {
  client: ClientWithTerritory;
  onClick?: () => void;
}

export function ClientCard({ client, onClick }: ClientCardProps) {
  return (
    <Card
      className="cursor-pointer transition-all hover:shadow-lg"
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-primary" />
              {client.client_name}
            </CardTitle>
            <CardDescription className="mt-1">
              {client.parent_org}
            </CardDescription>
          </div>
          <Badge variant={client.is_active ? "default" : "secondary"}>
            {client.is_active ? "Active" : "Inactive"}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Region and Segment */}
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span>{client.region}</span>
          </div>
          <Badge variant="outline">{client.segment}</Badge>
        </div>

        {/* Territory Assignment */}
        {client.territory_id && (
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Territory:</span>
            <Badge>{client.territory_id}</Badge>
          </div>
        )}

        {/* Advisor */}
        <div className="flex items-center gap-2 text-sm pt-3 border-t">
          <Mail className="h-4 w-4 text-muted-foreground" />
          <span className="text-muted-foreground truncate">
            {client.primary_advisor_email}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}

