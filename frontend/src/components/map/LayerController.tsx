import { BASEMAP_CONFIGS } from '@/config/basemaps'
import BaseMapSelector from './BaseMapSelector'
import type { BasemapConfig } from '@/config/types'

interface LayerControllerProps {
  selectedBasemap: BasemapConfig
  onBasemapChange: (basemap: BasemapConfig) => void
}

const LayerController = ({
  selectedBasemap,
  onBasemapChange,
}: LayerControllerProps) => {
  const handleBasemapChange = (basemapId: string) => {
    const basemap = BASEMAP_CONFIGS.find((b) => b.id === basemapId)
    if (basemap) {
      onBasemapChange(basemap)
    }
  }

  return (
    <div className="absolute top-4 right-4 z-[1000] bg-white p-4 rounded-lg shadow-lg">
      <BaseMapSelector
        basemaps={BASEMAP_CONFIGS}
        defaultValue={selectedBasemap.id}
        onValueChange={handleBasemapChange}
        name="basemap"
      />
    </div>
  )
}

export default LayerController
