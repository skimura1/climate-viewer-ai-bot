import type { BasemapConfig } from './types'

export const BASEMAP_CONFIGS: BasemapConfig[] = [
  {
    id: 'light',
    layerId: 'mapbox/light-v10',
    name: 'Light',
    description: 'Clean grayscale basemap',
    isDefault: true,
    category: 'street',
  },
  {
    id: 'satellite',
    layerId: 'mapbox/satellite-v9',
    name: 'Satellite',
    description: 'High-resolution satellite imagery',
    isDefault: false,
    category: 'satellite',
  },
  {
    id: 'hybrid',
    layerId: 'mapbox/satellite-streets-v11',
    name: 'Satellite Streets',
    description: 'Satellite with street labels',
    isDefault: false,
    category: 'satellite',
  },
]