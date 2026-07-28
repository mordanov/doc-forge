import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from './AppLayout'
import { AuthGuard } from './AuthGuard'

const LoginPage = lazy(() => import('@/features/auth/LoginPage'))
const HomePage = lazy(() => import('@/features/home/HomePage'))
const NewProjectWizard = lazy(() => import('@/features/wizard/NewProjectWizard'))
const ProjectsPage = lazy(() => import('@/features/projects/ProjectsPage'))
const ProjectDetailPage = lazy(() => import('@/features/projects/ProjectDetailPage'))
const SettingsPage = lazy(() => import('@/features/settings/SettingsPage'))
const AboutPage = lazy(() => import('@/features/about/AboutPage'))

function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-full min-h-[200px] text-muted-foreground text-sm">Loading…</div>}>
      {children}
    </Suspense>
  )
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <PageShell><LoginPage /></PageShell>,
  },
  {
    element: (
      <AuthGuard>
        <AppLayout />
      </AuthGuard>
    ),
    children: [
      { index: true, element: <PageShell><HomePage /></PageShell> },
      { path: 'projects/new', element: <PageShell><NewProjectWizard /></PageShell> },
      { path: 'projects', element: <PageShell><ProjectsPage /></PageShell> },
      { path: 'projects/:id', element: <PageShell><ProjectDetailPage /></PageShell> },
      { path: 'settings', element: <PageShell><SettingsPage /></PageShell> },
      { path: 'about', element: <PageShell><AboutPage /></PageShell> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
])
