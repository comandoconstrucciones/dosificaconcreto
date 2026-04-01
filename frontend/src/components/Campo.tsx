interface CampoProps {
  label: string
  name: string
  value: string | number
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
  type?: string
  step?: string
  min?: string
  max?: string
  children?: React.ReactNode
  ariaLabel?: string
}

export default function Campo({ label, name, value, onChange, type = 'number', step = '0.01', min, max, children, ariaLabel }: CampoProps) {
  return (
    <div>
      <label htmlFor={name} className="label">{label}</label>
      {children || (
        <input
          id={name}
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          step={step}
          min={min}
          max={max}
          className="input-field"
          aria-label={ariaLabel || label}
        />
      )}
    </div>
  )
}
