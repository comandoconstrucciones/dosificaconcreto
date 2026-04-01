interface BadgeProps {
  type: 'success' | 'danger'
  children: React.ReactNode
}

export default function Badge({ type, children }: BadgeProps) {
  const className = type === 'success' ? 'badge-success' : 'badge-danger'
  return <span className={className}>{children}</span>
}
