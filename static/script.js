// Global variables
let map;
let currentLocation = null;
let markers = [];
let isFullscreen = false;
let layerControl;
let baseLayers = {};
let overlayLayers = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  initializeMap();
  initializeChatbot();
  initializeEventListeners();
});

// Initialize Leaflet map
function initializeMap() {
  L.Map.include({
    _initControlPos: function() {
      var corners = this._controlCorners = {},
        l = 'leaflet-',
        container = this._controlContainer =
          L.DomUtil.create('div', l + 'control-container', this._container);

      function createCorner(vSide, hSide) {
        var className = l + vSide + ' ' + l + hSide;

        corners[vSide + hSide] = L.DomUtil.create('div', className, container);
      }

      createCorner('top', 'left');
      createCorner('top', 'right');
      createCorner('bottom', 'left');
      createCorner('bottom', 'right');

      createCorner('top', 'center');
      createCorner('middle', 'center');
      createCorner('middle', 'left');
      createCorner('middle', 'right');
      createCorner('bottom', 'center');
    }
  });

  // Set up map
  // Oʻahu zoom
  const zoomLevel = 11;
  const centerCoord = [21.483, -157.980];

  map = L.map('map', { preferCanvas: true, minZoom: 7, maxZoom: 19, dragging: !L.Browser.mobile }).setView(centerCoord, zoomLevel);

  // Restrict bounds to Hawaiʻi
  const southWest = L.latLng(15.2763, -166.7944);
  const northEast = L.latLng(25.3142, -148.3484);
  const bounds = L.latLngBounds(southWest, northEast);
  map.options.maxBounds = bounds;

  // Initialize base layers
  initializeBaseLayers();

  // Initialize WMS overlay layers
  initializeWMSLayers();

  // Add layer control
  layerControl = L.control.layers(baseLayers, overlayLayers, {
    collapsed: false,
    position: 'topright'
  }).addTo(map);

  // Handle map clicks
  map.on('click', function(e) {
    handleMapClick(e.latlng);
  });
}


// Get location name from coordinates
async function getLocationName(latlng) {
  try {
    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latlng.lat}&lon=${latlng.lng}&zoom=10`);
    const data = await response.json();
    return data.display_name.split(',')[0] || 'Unknown Location';
  } catch (error) {
    return 'Unknown Location';
  }
}

// Initialize chatbot functionality
function initializeChatbot() {
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-btn');
  const chatMessages = document.getElementById('chat-messages');

  // Auto-resize chat messages container
  function resizeChatMessages() {
    const headerHeight = document.querySelector('.chatbot-header').offsetHeight;
    const inputHeight = document.querySelector('.chat-input-container').offsetHeight;
    const containerHeight = document.querySelector('.chatbot-container').offsetHeight;
    chatMessages.style.maxHeight = `${containerHeight - headerHeight - inputHeight - 40}px`;
  }

  resizeChatMessages();
  window.addEventListener('resize', resizeChatMessages);
}

// Initialize event listeners
function initializeEventListeners() {
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-btn');
  const locateBtn = document.getElementById('locate-btn');
  const fullscreenBtn = document.getElementById('fullscreen-btn');
  const quickActionBtns = document.querySelectorAll('.quick-action-btn');

  // Send message on Enter key
  chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Send message on button click
  sendBtn.addEventListener('click', sendMessage);

  // Fullscreen button
  fullscreenBtn.addEventListener('click', toggleFullscreen);

  // Quick action buttons
  quickActionBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const prompt = this.getAttribute('data-prompt');
      chatInput.value = prompt;
      sendMessage();
    });
  });
}

// Send message function
function sendMessage() {
  const chatInput = document.getElementById('chat-input');
  const message = chatInput.value.trim();

  if (message) {
    addUserMessage(message);
    sendChatMessage(message);
    chatInput.value = '';
  }
}

// Add user message to chat
function addUserMessage(message) {
  const chatMessages = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message user-message';
  messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-user"></i>
        </div>
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Add bot message to chat
function addBotMessage(message) {
  const chatMessages = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message bot-message';
  messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Send message to AI service
async function sendChatMessage(message) {
  showLoading(true);

  try {
    const response = await AIResponse(message);
    const data = response.data
    const boundaries = data.boundaries
    const bounds = L.latLngBounds(
      [boundaries.south, boundaries.west], // Southwest
      [boundaries.north, boundaries.east]  // Northeast
    );

    overlayLayers[data.layer].addTo(map);
    map.fitBounds(bounds);

    addBotMessage(data.reason);
  } catch (error) {
    addBotMessage("I'm sorry, I'm having trouble processing your request right now. Please try again later.");
    console.error('Chat error:', error);
  } finally {
    showLoading(false);
  }
}

// Send Request to ChatAPI Endpoint
async function AIResponse(prompt) {
  const url = "http://127.0.0.1:8000/chat";
  const fetchData = {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ query: prompt }),
  }

  try {
    const response = await fetch(url, fetchData);

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // Rseponse Output:
    // { "layer": "HI_State_80prob_9ft_GWI", "foot_increment": 9, "reason": "Statewide flooding data at the 9 foot level as specifically requested." }
    // TODO: Validate format of the response probably serverside
    const jsonData = await response.json();
    return jsonData;
  }
  catch (error) {
    console.log(error);
    return null;
  }
}


// Toggle fullscreen
function toggleFullscreen() {
  const mapContainer = document.querySelector('.map-container');

  if (!isFullscreen) {
    mapContainer.style.position = 'fixed';
    mapContainer.style.top = '0';
    mapContainer.style.left = '0';
    mapContainer.style.width = '100vw';
    mapContainer.style.height = '100vh';
    mapContainer.style.zIndex = '9999';
    mapContainer.style.borderRadius = '0';
    document.body.style.overflow = 'hidden';
    isFullscreen = true;

    // Update button
    document.getElementById('fullscreen-btn').innerHTML = '<i class="fas fa-compress"></i>';
    document.getElementById('fullscreen-btn').title = 'Exit Fullscreen';

    // Trigger map resize
    setTimeout(() => map.invalidateSize(), 100);
  } else {
    mapContainer.style.position = 'relative';
    mapContainer.style.top = '';
    mapContainer.style.left = '';
    mapContainer.style.width = '';
    mapContainer.style.height = '';
    mapContainer.style.zIndex = '';
    mapContainer.style.borderRadius = '';
    document.body.style.overflow = '';
    isFullscreen = false;

    // Update button
    document.getElementById('fullscreen-btn').innerHTML = '<i class="fas fa-expand"></i>';
    document.getElementById('fullscreen-btn').title = 'Fullscreen';

    // Trigger map resize
    setTimeout(() => map.invalidateSize(), 100);
  }
}

// Utility functions
function scrollToBottom() {
  const chatMessages = document.getElementById('chat-messages');
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoading(show) {
  const loadingOverlay = document.getElementById('loading-overlay');
  if (show) {
    loadingOverlay.classList.remove('hidden');
  } else {
    loadingOverlay.classList.add('hidden');
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Handle escape key for fullscreen
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape' && isFullscreen) {
    toggleFullscreen();
  }
});

// Initialize base layers
function initializeBaseLayers() {

  // OpenStreetMap
  baseLayers['OpenStreetMap'] = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  });

  // Satellite imagery
  baseLayers['Satellite'] = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '© Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
  });

  // Terrain
  baseLayers['Terrain'] = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenTopoMap contributors'
  });

  // Dark theme
  baseLayers['Dark'] = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© CartoDB'
  });

  // Add default base layer to map
  baseLayers['OpenStreetMap'].addTo(map);
}

// Initialize WMS overlay layers
function initializeWMSLayers() {
  // Sample WMS layers for climate data
  const wmsLayers = [];

  const gwi_layer_config = (ft) => {
    return {
      tiled: true,
      transparent: true,
      opacity: 0.7,
      maxZoom: 19,
      srs: 'EPSG:3857',
      format: 'image/png',
      name: ft != 10 ? `Passive GWI 0${ft} ft all-scenarios` : `Passive GWI ${ft} ft all-scenarios`,
      url: 'https://crcgeo.soest.hawaii.edu/geoserver/gwc/service/wms',
      layers: ft != 10 ? `CRC:HI_State_80prob_0${ft}ft_GWI` : `CRC:HI_State_80prob_${ft}ft_GWI`,
    }
  };

  for (let i = 0; i < 11; i++) {
    wmsLayers.push(gwi_layer_config(i));
  }


  // Create WMS layers and add to overlay layers
  wmsLayers.forEach(layerConfig => {
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
        version: '1.3.0'
      });

      overlayLayers[layerConfig.name] = wmsLayer;
    } catch (error) {
      console.warn(`Failed to load WMS layer: ${layerConfig.name}`, error);
    }
  });
}
