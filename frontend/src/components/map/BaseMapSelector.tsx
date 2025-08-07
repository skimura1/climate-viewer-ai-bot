import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import type { BasemapConfig } from '@/config/types'

interface BaseMapSelectorProps {
  basemaps: BasemapConfig[]
  defaultValue: string
  onValueChange: (value: string) => void
  name: string
}

const BaseMapSelector = ({
  basemaps,
  defaultValue,
  onValueChange,
  name,
}: BaseMapSelectorProps) => {
  return (
    <div className="space-y-2">
      <Label className="text-sm font-medium">Basemap</Label>
      <RadioGroup
        defaultValue={defaultValue}
        onValueChange={onValueChange}
        name={name}
      >
        {basemaps.map((basemap) => (
          <div key={basemap.id} className="flex items-center space-x-2">
            <RadioGroupItem value={basemap.id} id={basemap.id} />
            <Label htmlFor={basemap.id} className="text-sm">
              {basemap.name}
            </Label>
          </div>
        ))}
      </RadioGroup>
    </div>
  )
}

export default BaseMapSelector
