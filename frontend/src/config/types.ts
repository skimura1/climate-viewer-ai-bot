export interface Coordinates {
  lat: number
  lng: number
}

export interface MapBounds {
  southwest: [number, number]
  northeast: [number, number]
}

export interface MapSettings {
  zoomLevel: number
  minZoom: number
  maxZoom: number
  preferCanvas: boolean
}

export interface MapboxConfig {
  url: string
  attribution: string
  accessToken: string
  options: {
    maxZoom: number
    tileSize: number
    zoomOffset: number
  }
}

export interface WMSConfig {
  url: string
  options: {
    tiled: boolean
    format: string
    attribution: string
    version: string
    transparent: boolean
    maxZoom: number
  }
}

export interface WMSLayers {
  tiled: boolean
  version: string
  format: 'image/png' | 'image/jpeg' | 'image/gif' | 'image/webp'
  transparent: boolean
  opacity: number
  errorTileUrl?: string
  attribution: string
  bounds: [[number, number], [number, number]] // [[south, west], [north, east]]
  maxZoom: number
  layers: string
  name: string
}

export interface WFSConfig {
  url: (layerName: string) => string
  options: {
    attribution: string
  }
}

export interface MVTConfig {
  url: (layerName: string) => string
}

export interface MapConfig {
  center: Coordinates
  hawaii: {
    honolulu: Coordinates
    maui: Coordinates
    bigIsland: Coordinates
    kauai: Coordinates
  }
  settings: MapSettings
  bounds: [number, number][]
  mapbox: MapboxConfig
  crcgeoWMS: WMSConfig
  crcgeoWFS: WFSConfig
  crcgeoMVT: MVTConfig
}

export interface BasemapConfig {
  id: string
  layerId: string
  name: string
  description?: string
  isDefault: boolean
  category: 'street' | 'satellite' | 'hybrid'
}

export interface ActiveLayersState {
  [layerId: string]: boolean
}
