// Map management module
export class MapManager {
	constructor() {
		this.map = null;
		this.currentLocation = null;
		this.markers = [];
		this.isFullscreen = false;
		this.layerControl = null;
		this.baseLayers = {};
		this.overlayLayers = {};
		this.activeLayer = new Set();
		this.footIncrement = "3";
	}

	initializeMap() {
		L.Map.include({
			_initControlPos: function () {
				var corners = (this._controlCorners = {}),
					l = "leaflet-",
					container = (this._controlContainer = L.DomUtil.create(
						"div",
						l + "control-container",
						this._container,
					));

				function createCorner(vSide, hSide) {
					var className = l + vSide + " " + l + hSide;
					corners[vSide + hSide] = L.DomUtil.create(
						"div",
						className,
						container,
					);
				}

				createCorner("top", "left");
				createCorner("top", "right");
				createCorner("bottom", "left");
				createCorner("bottom", "right");
				createCorner("top", "center");
				createCorner("middle", "center");
				createCorner("middle", "left");
				createCorner("middle", "right");
				createCorner("bottom", "center");
			},
		});

		// Set up map - Oʻahu zoom
		const zoomLevel = 11;
		const centerCoord = [21.483, -157.98];

		this.map = L.map("map", {
			preferCanvas: true,
			minZoom: 7,
			maxZoom: 19,
			dragging: !L.Browser.mobile,
		}).setView(centerCoord, zoomLevel);

		// Restrict bounds to Hawaiʻi
		const southWest = L.latLng(15.2763, -166.7944);
		const northEast = L.latLng(25.3142, -148.3484);
		const bounds = L.latLngBounds(southWest, northEast);
		this.map.options.maxBounds = bounds;

		// Initialize layers
		this.initializeBaseLayers();
		this.initializeWMSLayers();

		// Add layer control
		this.layerControl = L.control
			.layers(this.baseLayers, this.overlayLayers, {
				collapsed: false,
				position: "topright",
			})
			.addTo(this.map);

		this.map.on("layeradd", (e) => {
			const layer = e.layer.options.name;
			this.activeLayer.add(layer);
		});

		this.map.on("layerremove", (e) => {
			const layer = e.layer.options.name;
			this.activeLayer.delete(layer);
		});

		return this.map;
	}

	initializeBaseLayers() {
		// OpenStreetMap
		this.baseLayers["OpenStreetMap"] = L.tileLayer(
			"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
			{
				attribution: "© OpenStreetMap contributors",
			},
		);

		// Satellite imagery
		this.baseLayers["Satellite"] = L.tileLayer(
			"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
			{
				attribution:
					"© Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
			},
		);

		// Terrain
		this.baseLayers["Terrain"] = L.tileLayer(
			"https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
			{
				attribution: "© OpenTopoMap contributors",
			},
		);

		// Dark theme
		this.baseLayers["Dark"] = L.tileLayer(
			"https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
			{
				attribution: "© CartoDB",
			},
		);

		// Add default base layer to map
		this.baseLayers["OpenStreetMap"].addTo(this.map);
	}

	initializeWMSLayers() {
		const wmsLayers = [];

		const gwi_layer_config = (ft) => {
			return {
				tiled: true,
				transparent: true,
				opacity: 0.7,
				maxZoom: 19,
				srs: "EPSG:3857",
				format: "image/png",
				name:
					ft != 10
						? `Passive GWI 0${ft} ft all-scenarios`
						: `Passive GWI ${ft} ft all-scenarios`,
				url: "https://crcgeo.soest.hawaii.edu/geoserver/gwc/service/wms",
				layers:
					ft != 10
						? `CRC:HI_State_80prob_0${ft}ft_GWI`
						: `CRC:HI_State_80prob_${ft}ft_GWI`,
			};
		};

		for (let i = 0; i < 11; i++) {
			wmsLayers.push(gwi_layer_config(i));
		}

		// Create WMS layers and add to overlay layers
		wmsLayers.forEach((layerConfig) => {
			try {
				const wmsLayer = L.tileLayer.wms(layerConfig.url, {
					tiled: layerConfig.tiled,
					layers: layerConfig.layers,
					maxZoom: layerConfig.maxZoom,
					format: layerConfig.format,
					srs: layerConfig.srs,
					transparent: layerConfig.transparent,
					opacity: layerConfig.opacity,
					attribution: layerConfig.attribution,
					version: "1.3.0",
					name: layerConfig.name,
				});

				this.overlayLayers[layerConfig.name] = wmsLayer;
			} catch (error) {
				console.warn(`Failed to load WMS layer: ${layerConfig.name}`, error);
			}
		});
	}

	toggleFullscreen() {
		const mapContainer = document.querySelector(".map-container");

		if (!this.isFullscreen) {
			mapContainer.style.position = "fixed";
			mapContainer.style.top = "0";
			mapContainer.style.left = "0";
			mapContainer.style.width = "100vw";
			mapContainer.style.height = "100vh";
			mapContainer.style.zIndex = "9999";
			mapContainer.style.borderRadius = "0";
			document.body.style.overflow = "hidden";
			this.isFullscreen = true;

			// Update button
			document.getElementById("fullscreen-btn").innerHTML =
				'<i class="fas fa-compress"></i>';
			document.getElementById("fullscreen-btn").title = "Exit Fullscreen";

			// Trigger map resize
			setTimeout(() => this.map.invalidateSize(), 100);
		} else {
			mapContainer.style.position = "relative";
			mapContainer.style.top = "";
			mapContainer.style.left = "";
			mapContainer.style.width = "";
			mapContainer.style.height = "";
			mapContainer.style.zIndex = "";
			mapContainer.style.borderRadius = "";
			document.body.style.overflow = "";
			this.isFullscreen = false;

			// Update button
			document.getElementById("fullscreen-btn").innerHTML =
				'<i class="fas fa-expand"></i>';
			document.getElementById("fullscreen-btn").title = "Fullscreen";

			// Trigger map resize
			setTimeout(() => this.map.invalidateSize(), 100);
		}
	}

	async getLocationName(latlng) {
		try {
			const response = await fetch(
				`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latlng.lat}&lon=${latlng.lng}&zoom=10`,
			);
			const data = await response.json();
			return data.display_name.split(",")[0] || "Unknown Location";
		} catch (error) {
			return "Unknown Location";
		}
	}

	getMap() {
		return this.map;
	}

	getOverlayLayers() {
		return this.overlayLayers;
	}

	getActiveLayers() {
		return this.activeLayer;
	}

	getFootIncrement() {
		return this.footIncrement;
	}
	currentMapPosition() {
		const center = this.map.getCenter();
		const centerData = {
			lat: center.lat,
			long: center.lng,
		};
		return centerData;
	}
	getCurrentMapBounds() {
		const bounds = this.map.getBounds();
		return {
			north: bounds.getNorth(),
			south: bounds.getSouth(),
			east: bounds.getEast(),
			west: bounds.getWest(),
		};
	}

	getCurrentZoom() {
		return this.map.getZoom();
	}
}
