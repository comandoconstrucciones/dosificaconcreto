interface ResultCardProps {
  label: string
  value: string | number
  unit?: string
  sub?: string
}

export default function ResultCard({ label, value, unit, sub }: ResultCardProps) {
  return (
    <div className="result-card">
      <div className="text-xs text-blue-200 mb-1">{label}</div>
      <div className="text-2xl font-bold">
        {value} <span className="text-sm font-normal">{unit}</span>
      </div>
      {sub && <div className="text-xs text-blue-200 mt-1">{sub}</div>}
    </div>
  )
}
