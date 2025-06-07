import { Input } from '@/components/shadcn/input'
import { Label } from '@/components/shadcn/label'

interface LoginInputProps {
  id: string
  name: string
  type: string
  label: string
  placeholder: string
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  required?: boolean
  disabled?: boolean
  autoComplete?: string
}

export default function LoginInput({
  id,
  name,
  type,
  label,
  placeholder,
  value,
  onChange,
  required = false,
  disabled = false,
  autoComplete,
}: LoginInputProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id} className="text-sm font-medium text-gray-700">
        {label}
      </Label>
      <Input
        id={id}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        autoComplete={autoComplete}
        className="w-full [&:-webkit-autofill]:bg-transparent [&:-webkit-autofill]:shadow-[inset_0_0_0px_1000px_rgb(255,255,255)]"
      />
    </div>
  )
}
