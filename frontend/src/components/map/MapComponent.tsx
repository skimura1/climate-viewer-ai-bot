import L from 'leaflet'
import { useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'
import { MAP_CONFIG } from '@/config'
import { GWI_LAYERS } from '@/config/wmslayers'
import type { BasemapConfig, ActiveLayersState, MapBounds } from '@/config/types'

interface MapComponentProps {
  selectedBasemap: BasemapConfig
  activeLayers: ActiveLayersState
  mapPosition: MapBounds
  zoomLevel: number
}

const MapComponent = ({ selectedBasemap, activeLayers, mapPosition, zoomLevel }: MapComponentProps) => {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const basemapLayerRef = useRef<L.TileLayer | null>(null)
  const dataLayersRef = useRef<Map<string, L.TileLayer>>(new Map())
  const isUserInteractionRef = useRef(false)

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return

    // Initialize Map,
    const map = L.map(mapRef.current, {
      preferCanvas: MAP_CONFIG.settings.preferCanvas,
      minZoom: MAP_CONFIG.settings.minZoom,
      maxZoom: MAP_CONFIG.settings.maxZoom,
    }).setView(
      [MAP_CONFIG.center.lat, MAP_CONFIG.center.lng],
      MAP_CONFIG.settings.zoomLevel,
    )

    map.setMaxBounds(MAP_CONFIG.bounds)

    // Track user interactions
    map.on('movestart', () => {
      isUserInteractionRef.current = true
    })

    map.on('moveend', () => {
      // Reset after a short delay to allow for programmatic changes
      setTimeout(() => {
        isUserInteractionRef.current = false
      }, 100)
    })

    map.on('zoomstart', () => {
      isUserInteractionRef.current = true
    })

    map.on('zoomend', () => {
      // Reset after a short delay to allow for programmatic changes
      setTimeout(() => {
        isUserInteractionRef.current = false
      }, 100)
    })

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
  }, [])

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

  // Handle data layer changes
  useEffect(() => {
    if (!mapInstanceRef.current) return

    const map = mapInstanceRef.current
    const currentLayers = dataLayersRef.current
    // Process each layer in activeLayers
    Object.entries(activeLayers).forEach(([layerId, isActive]) => {
      const existingLayer = currentLayers.get(layerId)
      
      if (isActive && !existingLayer) {
        // Add new layer
        const layerConfig = GWI_LAYERS.find(layer => layer.layers === layerId)
        if (layerConfig && MAP_CONFIG.crcgeoWMS) {
          const wmsLayer = L.tileLayer.wms(MAP_CONFIG.crcgeoWMS.url, {
            layers: layerConfig.layers,
            format: layerConfig.format,
            transparent: layerConfig.transparent,
            version: layerConfig.version,
            opacity: layerConfig.opacity,
            maxZoom: layerConfig.maxZoom,
            attribution: layerConfig.attribution,
          })
          
          wmsLayer.addTo(map)
          currentLayers.set(layerId, wmsLayer)
        }
      } else if (!isActive && existingLayer) {
        // Remove existing layer
        map.removeLayer(existingLayer)
        currentLayers.delete(layerId)
      }
    })

    // Clean up layers that are no longer in activeLayers
    currentLayers.forEach((layer, layerId) => {
      if (!(layerId in activeLayers)) {
        map.removeLayer(layer)
        currentLayers.delete(layerId)
      }
    })
  }, [activeLayers])

  // Handle programmatic map position changes (from chatbot)
  useEffect(() => {
    if (!mapInstanceRef.current || isUserInteractionRef.current) return
    
    const map = mapInstanceRef.current
    
    // Use bounds for better area coverage
    if (mapPosition.southwest && mapPosition.northeast) {
      const bounds: [[number, number], [number, number]] = [
        mapPosition.southwest,  // Southwest [lat, lng]
        mapPosition.northeast   // Northeast [lat, lng]
      ]
      map.fitBounds(bounds, { 
        animate: true,
        padding: [20, 20] // Add padding around the bounds
      })
    }
  }, [mapPosition])

  // Handle programmatic zoom changes (from chatbot)
  useEffect(() => {
    if (!mapInstanceRef.current || isUserInteractionRef.current) return
    
    const map = mapInstanceRef.current
    map.setZoom(zoomLevel, { animate: true })
  }, [zoomLevel])

  return <div ref={mapRef} className="h-full w-full" />
}

export default MapComponent
