import { BASEMAP_CONFIGS } from '@/config/basemaps'
import BaseMapSelector from './BaseMapSelector'
import type { BasemapConfig, ActiveLayersState } from '@/config/types'
import DataLayerSelector from './DataLayerSelector'

interface LayerControllerProps {
  selectedBasemap: BasemapConfig
  onBasemapChange: (basemap: BasemapConfig) => void
  activeLayers: ActiveLayersState
  onLayerToggle: (layerId: string, isActive: boolean) => void
}

const LayerController = ({
  selectedBasemap,
  onBasemapChange,
  activeLayers,
  onLayerToggle,
}: LayerControllerProps) => {
  const handleBasemapChange = (basemapId: string) => {
    const basemap = BASEMAP_CONFIGS.find((b) => b.id === basemapId)
    if (basemap) {
      onBasemapChange(basemap)
    }
  }

  return (
    <div className="absolute top-4 right-4 z-[1000] bg-white p-4 rounded-lg shadow-lg space-y-4">
      <BaseMapSelector
        basemaps={BASEMAP_CONFIGS}
        defaultValue={selectedBasemap.id}
        onValueChange={handleBasemapChange}
        name="basemap"
      />
      <DataLayerSelector 
        activeLayers={activeLayers}
        onLayerToggle={onLayerToggle}
      />
    </div>
  )
}

export default LayerController
