import L from 'leaflet'
import { useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'
import { MAP_CONFIG } from '@/config'
import type { BasemapConfig } from '@/config/types'

interface MapComponentProps {
  selectedBasemap: BasemapConfig
}

const MapComponent = ({ selectedBasemap }: MapComponentProps) => {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const basemapLayerRef = useRef<L.TileLayer | null>(null)

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return

    const map = L.map(mapRef.current, {
      preferCanvas: MAP_CONFIG.settings.preferCanvas,
      minZoom: MAP_CONFIG.settings.minZoom,
      maxZoom: MAP_CONFIG.settings.maxZoom,
    }).setView(
      [MAP_CONFIG.center.lat, MAP_CONFIG.center.lng],
      MAP_CONFIG.settings.zoomLevel,
    )

    map.setMaxBounds(MAP_CONFIG.bounds)

    // Add initial basemap
    const basemapUrl = MAP_CONFIG.mapbox.url
      .replace('{id}', selectedBasemap.layerId)
      .replace('{accessToken}', MAP_CONFIG.mapbox.accessToken)

    const basemapLayer = L.tileLayer(basemapUrl, {
      attribution: MAP_CONFIG.mapbox.attribution,
      ...MAP_CONFIG.mapbox.options,
    })

    basemapLayer.addTo(map)
    basemapLayerRef.current = basemapLayer

    mapInstanceRef.current = map

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [selectedBasemap])

  // Handle basemap changes
  useEffect(() => {
    if (!mapInstanceRef.current || !basemapLayerRef.current) return

    // Remove current basemap
    mapInstanceRef.current.removeLayer(basemapLayerRef.current)

    // Add new basemap
    const basemapUrl = MAP_CONFIG.mapbox.url
      .replace('{id}', selectedBasemap.layerId)
      .replace('{accessToken}', MAP_CONFIG.mapbox.accessToken)

    const newBasemapLayer = L.tileLayer(basemapUrl, {
      attribution: MAP_CONFIG.mapbox.attribution,
      ...MAP_CONFIG.mapbox.options,
    })

    newBasemapLayer.addTo(mapInstanceRef.current)
    basemapLayerRef.current = newBasemapLayer
  }, [selectedBasemap])

  return <div ref={mapRef} className="h-full w-full" />
}

export default MapComponent
