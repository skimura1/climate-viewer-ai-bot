import { useState } from 'react'
import MapComponent from './MapComponent'
import LayerController from './LayerController'
import { BASEMAP_CONFIGS } from '@/config/basemaps'
import type { BasemapConfig, ActiveLayersState } from '@/config/types'

const MapContainer = () => {
  const [selectedBasemap, setSelectedBasemap] = useState<BasemapConfig>(
    BASEMAP_CONFIGS.find((b) => b.isDefault) || BASEMAP_CONFIGS[0],
  )
  const [activeLayers, setActiveLayers] = useState<ActiveLayersState>({})

  const handleLayerToggle = (layerId: string, isActive: boolean) => {
    setActiveLayers(prev => ({
      ...prev,
      [layerId]: isActive
    }))
  }

  return (
    <div className="relative h-screen w-full">
      <MapComponent 
        selectedBasemap={selectedBasemap} 
        activeLayers={activeLayers}
      />
      <LayerController
        selectedBasemap={selectedBasemap}
        onBasemapChange={setSelectedBasemap}
        activeLayers={activeLayers}
        onLayerToggle={handleLayerToggle}
      />
    </div>
  )
}

export default MapContainer

