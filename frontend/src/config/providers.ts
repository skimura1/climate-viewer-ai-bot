import type { MapboxConfig, WMSConfig, WFSConfig, MVTConfig } from './types'

export const MAPBOX_CONFIG: MapboxConfig = {
  url: 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}',
  attribution:
    '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  accessToken: import.meta.env.VITE_MAPBOX_ACCESS_TOKEN,
  options: {
    maxZoom: 19,
    tileSize: 512,
    zoomOffset: -1,
  },
}

export const CRC_GEO_WMS_CONFIG: WMSConfig = {
  url: 'https://crcgeo.soest.hawaii.edu/geoserver/gwc/service/wms',
  options: {
    tiled: true,
    format: 'image/png',
    attribution:
      'Data &copy; <a href="https://www.soest.hawaii.edu/crc/" target="_blank" title="Climate Resilience Collaborative at University of Hawaii (UH) School of Ocean and Earth Science and Technology (SOEST)">UH/SOEST/CRC</a>',
    version: '1.1.1',
    transparent: true,
    maxZoom: 19,
  },
}

export const CRC_GEO_WFS_CONFIG: WFSConfig = {
  url: (layerName: string): string =>
    `https://crcgeo.soest.hawaii.edu/geoserver/CRC/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=${layerName}&outputFormat=application%2Fjson&srsName=EPSG:4326`,
  options: {
    attribution:
      'Data &copy; <a href="https://www.soest.hawaii.edu/crc/" target="_blank" title="Climate Resilience Collaborative at University of Hawaii (UH) School of Ocean and Earth Science and Technology (SOEST)">UH/SOEST/CRC</a>',
  },
}

export const CRC_GEO_MVT_CONFIG: MVTConfig = {
  url: (layerName: string): string =>
    `https://crcgeo.soest.hawaii.edu/geoserver/gwc/service/tms/1.0.0/${layerName}@EPSG%3A900913@pbf/{z}/{x}/{-y}.pbf`,
}

