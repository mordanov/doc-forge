import { NavLink, Outlet } from 'react-router-dom'
import { Home, FolderOpen, Settings, Info, FilePlus } from 'lucide-react'
import { useMediaQuery } from '@/hooks/useMediaQuery'
import { cn } from '@/lib/utils'
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import { LangSwitch } from '@/components/LangSwitch'
import { useT } from '@/hooks/useT'

export function AppLayout() {
  const collapsed = !useMediaQuery('(min-width: 1024px)')
  const t = useT()

  const NAV_ITEMS = [
    { to: '/', icon: Home, label: t.nav.home, end: true },
    { to: '/projects/new', icon: FilePlus, label: t.nav.newProject },
    { to: '/projects', icon: FolderOpen, label: t.nav.projects },
    { to: '/settings', icon: Settings, label: t.nav.settings },
    { to: '/about', icon: Info, label: t.nav.about },
  ]

  return (
    <TooltipProvider delayDuration={200}>
      <div className="flex min-h-screen bg-background">
        <aside
          className={cn(
            'flex flex-col border-r bg-card transition-all duration-200',
            collapsed ? 'w-16' : 'w-56'
          )}
        >
          <div className={cn('flex items-center h-14 px-4 border-b font-bold text-lg', collapsed && 'justify-center px-0')}>
            {collapsed ? 'DF' : t.appName}
          </div>
          <nav className="flex flex-col gap-1 p-2 flex-1">
            {NAV_ITEMS.map(({ to, icon: Icon, label, end }) => (
              collapsed ? (
                <Tooltip key={to}>
                  <TooltipTrigger asChild>
                    <NavLink
                      to={to}
                      end={end}
                      className={({ isActive }) =>
                        cn('flex items-center justify-center h-10 rounded-md transition-colors hover:bg-accent', isActive && 'bg-accent text-accent-foreground font-medium')
                      }
                      aria-label={label}
                    >
                      <Icon className="h-5 w-5" />
                    </NavLink>
                  </TooltipTrigger>
                  <TooltipContent side="right">{label}</TooltipContent>
                </Tooltip>
              ) : (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  className={({ isActive }) =>
                    cn('flex items-center gap-3 h-10 px-3 rounded-md transition-colors hover:bg-accent text-sm', isActive && 'bg-accent text-accent-foreground font-medium')
                  }
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {label}
                </NavLink>
              )
            ))}
          </nav>
          <div className={cn('flex items-center border-t p-3', collapsed ? 'justify-center' : 'px-4')}>
            <LangSwitch />
          </div>
        </aside>
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </TooltipProvider>
  )
}
