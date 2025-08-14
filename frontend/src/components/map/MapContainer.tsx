import { useState } from 'react'
import MapComponent from './MapComponent'
import LayerController from './LayerController'
import Chat from '../chat/Chat'
import { BASEMAP_CONFIGS } from '@/config/basemaps'
import type { BasemapConfig, ActiveLayersState } from '@/config/types'
import type { MapBounds } from '@/config/types'
import { MAP_CONFIG } from '@/config'

const MapContainer = () => {
  const [selectedBasemap, setSelectedBasemap] = useState<BasemapConfig>(
    BASEMAP_CONFIGS.find((b) => b.isDefault) || BASEMAP_CONFIGS[0],
  )
  const [activeLayers, setActiveLayers] = useState<ActiveLayersState>({})
  const [mapPosition, setMapPosition] = useState<MapBounds>({
    southwest: MAP_CONFIG.bounds[0],
    northeast: MAP_CONFIG.bounds[1],
  })
  const [zoomLevel, setZoomLevel] = useState(MAP_CONFIG.settings.zoomLevel)

  const handleLayerToggle = (layerId: string, isActive: boolean) => {
    console.log(`Toggling layer ${layerId} to ${isActive}`)
    setActiveLayers(prev => ({
      ...prev,
      [layerId]: isActive
    }))
  }

  // TODO: Get zoom level, map position, level increment from map component
  return (
    <div className="relative h-screen w-full">
      <MapComponent 
        selectedBasemap={selectedBasemap} 
        activeLayers={activeLayers}
        mapPosition={mapPosition}
        zoomLevel={zoomLevel}
      />
      <LayerController
        selectedBasemap={selectedBasemap}
        onBasemapChange={setSelectedBasemap}
        activeLayers={activeLayers}
        onLayerToggle={handleLayerToggle}
      />
      <Chat 
        activeLayers={activeLayers}
        toggleLayer={handleLayerToggle}
        mapPosition={mapPosition}
        zoomLevel={zoomLevel}
        setMapPosition={setMapPosition}
        setZoomLevel={setZoomLevel}
        setSelectedBasemap={setSelectedBasemap}
        selectedBasemap={selectedBasemap}
      />
    </div>
  )
}

export default MapContainer

