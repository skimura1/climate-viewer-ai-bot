import L from 'leaflet'
import { useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'

const MapComponent = () => {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return

    // Initialize map centered on Honolulu
    const map = L.map(mapRef.current, {
      center: [21.3099, -157.8581], // Honolulu coordinates
      zoom: 10,
      zoomControl: false,
    })

    // Fix for default markers
    delete (
      L.Icon.Default.prototype as unknown as { _getIconUrl?: () => string }
    )._getIconUrl
    L.Icon.Default.mergeOptions({
      iconRetinaUrl:
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl:
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl:
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    })

    // Basemap layers
    const baseMaps = {
      OpenStreetMap: L.tileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {
          maxZoom: 19,
          attribution: '© OpenStreetMap contributors',
        },
      ),
      Satellite: L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {
          maxZoom: 19,
          attribution:
            'Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community',
        },
      ),
      Topographic: L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        {
          maxZoom: 19,
          attribution:
            'Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community',
        },
      ),
    }

    // Data layers
    const dataLayers = {
      'Climate Stations': L.layerGroup([
        L.marker([21.3182, -157.8066]).bindPopup(
          'Honolulu Climate Station<br>Temperature: 78°F<br>Humidity: 65%',
        ),
        L.marker([21.4389, -158.0001]).bindPopup(
          'Pearl Harbor Station<br>Temperature: 76°F<br>Humidity: 68%',
        ),
        L.marker([21.2777, -157.8262]).bindPopup(
          'Diamond Head Station<br>Temperature: 79°F<br>Humidity: 62%',
        ),
      ]),
      'Weather Data': L.layerGroup([
        L.circle([21.3099, -157.8581], {
          color: 'blue',
          fillColor: '#30f',
          fillOpacity: 0.3,
          radius: 5000,
        }).bindPopup('Temperature Zone: 75-80°F'),
        L.circle([21.4389, -158.0001], {
          color: 'green',
          fillColor: '#0f3',
          fillOpacity: 0.3,
          radius: 3000,
        }).bindPopup('Humidity Zone: 65-70%'),
      ]),
      'Ocean Data': L.layerGroup([
        L.polygon(
          [
            [21.25, -157.9],
            [21.35, -157.9],
            [21.35, -157.8],
            [21.25, -157.8],
          ],
          {
            color: 'cyan',
            fillColor: '#0ff',
            fillOpacity: 0.2,
          },
        ).bindPopup('Ocean Temperature: 77°F<br>Salinity: 35 ppt'),
      ]),
    }

    // Add default basemap
    baseMaps.OpenStreetMap.addTo(map)

    // Custom Layer Controller
    const CustomLayerControl = L.Control.extend({
      options: {
        position: 'topright',
      },

      onAdd: (map: L.Map) => {
        const container = L.DomUtil.create('div', 'custom-layer-control')
        container.style.backgroundColor = 'white'
        container.style.padding = '10px'
        container.style.border = '2px solid rgba(0,0,0,0.2)'
        container.style.borderRadius = '5px'
        container.style.boxShadow = '0 1px 5px rgba(0,0,0,0.4)'
        container.style.minWidth = '200px'

        // Prevent map events when interacting with control
        L.DomEvent.disableClickPropagation(container)
        L.DomEvent.disableScrollPropagation(container)

        // Basemap section
        const basemapTitle = L.DomUtil.create('h4', '', container)
        basemapTitle.innerHTML = 'Base Maps'
        basemapTitle.style.margin = '0 0 10px 0'
        basemapTitle.style.borderBottom = '1px solid #ccc'
        basemapTitle.style.paddingBottom = '5px'

        let activeBasemap = 'OpenStreetMap'

        Object.keys(baseMaps).forEach((name) => {
          const label = L.DomUtil.create('label', '', container)
          label.style.display = 'block'
          label.style.marginBottom = '5px'
          label.style.cursor = 'pointer'

          const radio = L.DomUtil.create('input', '', label) as HTMLInputElement
          radio.type = 'radio'
          radio.name = 'basemap'
          radio.value = name
          radio.checked = name === activeBasemap
          radio.style.marginRight = '5px'

          const text = L.DomUtil.create('span', '', label)
          text.innerHTML = name

          L.DomEvent.on(radio, 'change', () => {
            if (radio.checked) {
              // Remove current basemap
              Object.values(baseMaps).forEach((layer) => map.removeLayer(layer))
              // Add new basemap
              baseMaps[name as keyof typeof baseMaps].addTo(map)
              activeBasemap = name
            }
          })
        })

        // Data layers section
        const dataTitle = L.DomUtil.create('h4', '', container)
        dataTitle.innerHTML = 'Data Layers'
        dataTitle.style.margin = '15px 0 10px 0'
        dataTitle.style.borderBottom = '1px solid #ccc'
        dataTitle.style.paddingBottom = '5px'

        Object.keys(dataLayers).forEach((name) => {
          const label = L.DomUtil.create('label', '', container)
          label.style.display = 'block'
          label.style.marginBottom = '5px'
          label.style.cursor = 'pointer'

          const checkbox = L.DomUtil.create(
            'input',
            '',
            label,
          ) as HTMLInputElement
          checkbox.type = 'checkbox'
          checkbox.style.marginRight = '5px'

          const text = L.DomUtil.create('span', '', label)
          text.innerHTML = name

          L.DomEvent.on(checkbox, 'change', () => {
            const layer = dataLayers[name as keyof typeof dataLayers]
            if (checkbox.checked) {
              layer.addTo(map)
            } else {
              map.removeLayer(layer)
            }
          })
        })

        return container
      },
    })

    // Add custom layer control to map
    new CustomLayerControl().addTo(map)

    // Add zoom control to bottom right
    L.control.zoom({ position: 'bottomright' }).addTo(map)

    mapInstanceRef.current = map

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [])

  return (
    <div
      ref={mapRef}
      style={{
        height: '100vh',
        width: '100%',
      }}
    />
  )
}

export default MapComponent
