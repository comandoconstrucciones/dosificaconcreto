'use client'

import { Component, type ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="card max-w-lg mx-auto mt-12 text-center">
          <div className="text-4xl mb-4">Error</div>
          <h2 className="text-lg font-semibold text-red-700 mb-2">Algo salió mal</h2>
          <p className="text-sm text-gray-600 mb-4">
            Ocurrió un error inesperado. Por favor recarga la página.
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="btn-primary"
          >
            Intentar de nuevo
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
