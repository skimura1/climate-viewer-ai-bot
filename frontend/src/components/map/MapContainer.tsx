import { useState } from 'react'
import MapComponent from './MapComponent'
import LayerController from './LayerController'
import { BASEMAP_CONFIGS } from '@/config/basemaps'
import type { BasemapConfig } from '@/config/types'

const MapContainer = () => {
  const [selectedBasemap, setSelectedBasemap] = useState<BasemapConfig>(
    BASEMAP_CONFIGS.find((b) => b.isDefault) || BASEMAP_CONFIGS[0],
  )

  return (
    <div className="relative h-screen w-full">
      <MapComponent selectedBasemap={selectedBasemap} />
      <LayerController
        selectedBasemap={selectedBasemap}
        onBasemapChange={setSelectedBasemap}
      />
    </div>
  )
}

export default MapContainer

