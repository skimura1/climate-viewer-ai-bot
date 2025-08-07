import type { MapConfig } from './types'
import {
  MAPBOX_CONFIG,
  CRC_GEO_WMS_CONFIG,
  CRC_GEO_WFS_CONFIG,
  CRC_GEO_MVT_CONFIG,
} from './providers'

export const MAP_CONFIG: MapConfig = {
  // Default center: Honolulu, Hawaii
  center: {
    lat: 21.3099,
    lng: -157.8581,
  },

  // Hawaiian Islands coordinates for navigation
  hawaii: {
    honolulu: {
      lat: 21.3099,
      lng: -157.8581,
    },
    maui: {
      lat: 20.7984,
      lng: -156.3319,
    },
    bigIsland: {
      lat: 19.8968,
      lng: -155.5828,
    },
    kauai: {
      lat: 22.0964,
      lng: -159.5261,
    },
  },

  // Map settings
  settings: {
    zoomLevel: 12,
    minZoom: 7,
    maxZoom: 19,
    preferCanvas: true,
  },

  // Map bounds for Hawaiian Islands
  bounds: [
    [18.0, -162.0], // Southwest corner
    [23.0, -154.0], // Northeast corner
  ],

  mapbox: MAPBOX_CONFIG,
  crcgeoWMS: CRC_GEO_WMS_CONFIG,
  crcgeoWFS: CRC_GEO_WFS_CONFIG,
  crcgeoMVT: CRC_GEO_MVT_CONFIG,
}
