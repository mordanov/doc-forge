import React from 'react'
import { Button } from '@/components/ui/button'

interface Props {
  children: React.ReactNode
  onRetry?: () => void
}

interface State {
  hasError: boolean
  message: string
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, message: '' }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message }
  }

  render() {
    if (!this.state.hasError) return this.props.children

    return (
      <div className="flex flex-col items-center justify-center min-h-[200px] gap-4 p-8 text-center">
        <h2 className="text-lg font-semibold">Something went wrong</h2>
        <p className="text-sm text-muted-foreground max-w-md">{this.state.message}</p>
        <div className="flex gap-2">
          {this.props.onRetry && (
            <Button variant="outline" onClick={() => { this.setState({ hasError: false, message: '' }); this.props.onRetry?.() }}>
              Try again
            </Button>
          )}
          <Button variant="ghost" onClick={() => { window.location.href = '/' }}>
            Go home
          </Button>
        </div>
      </div>
    )
  }
}
