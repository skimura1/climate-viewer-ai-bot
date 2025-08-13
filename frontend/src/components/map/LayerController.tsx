import { BASEMAP_CONFIGS } from '@/config/basemaps'
import BaseMapSelector from './BaseMapSelector'
import type { BasemapConfig, ActiveLayersState } from '@/config/types'
import DataLayerSelector from './DataLayerSelector'
import { Button } from '../ui/button'
import { useState } from 'react'

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
  const [isOpen, setIsOpen] = useState(false)

  const handleBasemapChange = (basemapId: string) => {
    const basemap = BASEMAP_CONFIGS.find((b) => b.id === basemapId)
    if (basemap) {
      onBasemapChange(basemap)
    }
  }

  return (
    <div className="fixed top-4 right-4 z-[1001]">
      {!isOpen ? (
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="h-12 w-12 p-0 rounded-lg shadow-lg"
        >
          <svg
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m0 0L9 7"
            />
          </svg>
        </Button>
      ) : (
        <div className="bg-white p-4 rounded-lg shadow-lg space-y-4 min-w-[280px]">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold text-gray-800">Map Layers</h3>
            <Button
              onClick={() => setIsOpen(false)}
              size="sm"
              variant="ghost"
              className="h-6 w-6 p-0"
            >
              ×
            </Button>
          </div>
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
      )}
    </div>
  )
}

export default LayerController
