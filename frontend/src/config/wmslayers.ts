import type { WMSLayers } from './types'

const createPassiveLayers = (ft: number, type: string): WMSLayers => ({
  tiled: true,
  version: '1.1.1',
  format: 'image/png',
  transparent: true,
  opacity: 0.67,
  // errorTileUrl: 'http://www.soest.hawaii.edu/crc/SLRviewer/tile_error.png',
  attribution:
    'Data &copy; <a href="https://www.soest.hawaii.edu/crc/" target="_blank" title="Climate Resilience Collaborative at University of Hawaii (UH) School of Ocean and Earth Science and Technology (SOEST)">UH/SOEST/CRC</a>',
  bounds: [
    [18.86, -159.82],
    [22.26, -154.75],
  ],
  maxZoom: 19,
  layers:
    ft < 10
      ? `CRC:HI_State_80prob_0${ft}ft_${type}`
      : `CRC:HI_State_80prob_${ft}ft_${type}`,
  name:
    ft < 10
      ? `Passive ${type} 0${ft}ft all-scenarios`
      : `Passive ${type} ${ft}ft all-scenarios`,
})
const createPassiveLayersByType = (type: string): WMSLayers[] => {
  const layers: WMSLayers[] = []
  for (let i = 1; i <= 10; i++) {
    layers.push(createPassiveLayers(i, type))
  }
  return layers
}

export const PASSIVE_FLOODING_LAYERS = {
  SCI: createPassiveLayersByType('SCI'),
  GWI: createPassiveLayersByType('GWI'),
}

const createGWILayer = (ft: number): WMSLayers => ({
  tiled: true,
  version: '1.1.1',
  format: 'image/png',
  transparent: true,
  opacity: 0.67,
  attribution:
    'Data &copy; <a href="https://www.soest.hawaii.edu/crc/" target="_blank" title="Climate Resilience Collaborative at University of Hawaii (UH) School of Ocean and Earth Science and Technology (SOEST)">UH/SOEST/CRC</a>',
  bounds: [
    [18.86, -159.82],
    [22.26, -154.75],
  ],
  maxZoom: 19,
  layers: ft < 10 ? `CRC:HI_Oahu_GWI_0${ft}ft` : `CRC:HI_Oahu_GWI_${ft}ft`,
  name:
    ft < 10
      ? `Potential Groundwater inundation 0${ft}ft all-scenarios`
      : `Potential Groundwater inundation ${ft}ft all-scenarios`,
})

export const GWI_LAYERS: WMSLayers[] = []
for (let i = 1; i <= 10; i++) {
  GWI_LAYERS.push(createGWILayer(i))
}
