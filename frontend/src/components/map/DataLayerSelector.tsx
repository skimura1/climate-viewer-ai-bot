import { GWI_LAYERS } from '@/config/wmslayers'
import { Checkbox } from '../ui/checkbox'
import { Label } from '../ui/label'
import type { ActiveLayersState } from '@/config/types'

interface DataLayerSelectorProps {
  activeLayers: ActiveLayersState
  onLayerToggle: (layerId: string, isActive: boolean) => void
}

const DataLayerSelector = ({ activeLayers, onLayerToggle }: DataLayerSelectorProps) => {
  return (
    <div className="space-y-2">
      <Label className="text-sm font-medium">Data Layers</Label>
      {GWI_LAYERS.map((layer) => (
        <div key={layer.layers} className="flex items-center space-x-2">
          <Checkbox 
            id={layer.layers}
            checked={activeLayers[layer.layers] || false}
            onCheckedChange={(checked) => onLayerToggle(layer.layers, Boolean(checked))}
          />
          <Label htmlFor={layer.layers} className="text-sm">
            {layer.name}
          </Label>
        </div>
      ))}
    </div>
  )
}
export default DataLayerSelector
