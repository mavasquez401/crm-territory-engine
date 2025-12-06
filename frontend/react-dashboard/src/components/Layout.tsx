/**
 * Main Layout Component
 * 
 * Provides navigation sidebar and main content area
 */

import { Link, Outlet, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  MapPin, 
  Users, 
  UserCircle,
  Menu
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

// Navigation items
const navItems = [
  {
    title: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    title: 'Territories',
    href: '/territories',
    icon: MapPin,
  },
  {
    title: 'Clients',
    href: '/clients',
    icon: Users,
  },
  {
    title: 'Advisors',
    href: '/advisors',
    icon: UserCircle,
  },
]

export function Layout() {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen transition-transform",
          sidebarOpen ? "w-64" : "w-20"
        )}
      >
        <div className="flex h-full flex-col border-r bg-card">
          {/* Header */}
          <div className="flex h-16 items-center justify-between px-4 border-b">
            {sidebarOpen && (
              <h1 className="text-lg font-semibold">CRM Territory</h1>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="rounded-md p-2 hover:bg-accent"
            >
              <Menu className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href

              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {sidebarOpen && <span>{item.title}</span>}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="border-t p-4">
            {sidebarOpen && (
              <p className="text-xs text-muted-foreground">
                v1.0.0 • Enterprise CRM
              </p>
            )}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main
        className={cn(
          "transition-all",
          sidebarOpen ? "ml-64" : "ml-20"
        )}
      >
        {/* Top bar */}
        <header className="sticky top-0 z-30 flex h-16 items-center border-b bg-background px-6">
          <h2 className="text-xl font-semibold">
            {navItems.find((item) => item.href === location.pathname)?.title || 'Dashboard'}
          </h2>
        </header>

        {/* Page content */}
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
