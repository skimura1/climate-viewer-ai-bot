# Climate Viewer AI Bot Frontend

This project has been converted to use ES6 modules for better code organization and maintainability.

## Project Structure

```
frontend/
├── main.js                      # Main application entry point
├── modules/
│   ├── mapManager.js           # Map initialization and management
│   ├── chatManager.js          # Chat interface and AI communication
│   └── eventManager.js         # Event handling and user interactions
├── climate_viewer_tracker.js   # Layer tracking utility (ES6 module)
├── index.html                  # Main HTML file
├── styles.css                  # Styles
└── package.json               # Module configuration
```

## Module Overview

### MapManager (`modules/mapManager.js`)
- Handles Leaflet map initialization
- Manages base layers and WMS overlay layers
- Provides fullscreen functionality
- Handles location services

### ChatManager (`modules/chatManager.js`)
- Manages chat interface
- Handles AI communication with backend
- Processes user messages and bot responses
- Manages loading states

### EventManager (`modules/eventManager.js`)
- Handles map click events
- Manages keyboard shortcuts
- Coordinates user interface interactions

### ClimateViewerLayerTracker (`climate_viewer_tracker.js`)
- Tracks active map layers
- Provides layer management utilities
- Maintains map state information

## Running the Application

1. Start a local HTTP server:
   ```bash
   npm start
   # or
   python -m http.server 8080
   ```

2. Open your browser to `http://localhost:8080`

## ES6 Module Features

- **Import/Export**: Clean module boundaries with explicit imports and exports
- **Encapsulation**: Each module manages its own state and functionality
- **Maintainability**: Easier to understand, test, and modify individual components
- **Modern JavaScript**: Uses contemporary JavaScript patterns and syntax

## Browser Compatibility

This application requires a modern browser that supports ES6 modules (ES2015+). All major browsers released after 2017 support ES6 modules natively.