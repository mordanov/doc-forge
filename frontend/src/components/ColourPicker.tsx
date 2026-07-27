import { Label } from '@/components/ui/label'

interface ColourPickerProps {
  value: string | null
  onChange: (colour: string) => void
}

export function ColourPicker({ value, onChange }: ColourPickerProps) {
  return (
    <div className="flex items-center gap-3">
      <Label htmlFor="custom-colour" className="text-sm">Custom colour</Label>
      <input
        id="custom-colour"
        type="color"
        value={value ?? '#000000'}
        onChange={(e) => onChange(e.target.value)}
        className="h-9 w-16 rounded border cursor-pointer bg-transparent"
        aria-label="Pick custom colour"
      />
      {value && (
        <span className="text-xs text-muted-foreground font-mono">{value}</span>
      )}
    </div>
  )
}
