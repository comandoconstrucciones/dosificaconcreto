interface AlertBannerProps {
  type: 'warning' | 'danger'
  children: React.ReactNode
}

export default function AlertBanner({ type, children }: AlertBannerProps) {
  const className = type === 'warning' ? 'alert-warning' : 'alert-danger'
  return <div className={className}>{children}</div>
}
