// Main application entry point
import { MapManager } from "./src/mapManager.js";
import { ChatManager } from "./src/chatManager.js";
import { EventManager } from "./src/eventManager.js";

class ClimateViewerApp {
	constructor() {
		this.mapManager = null;
		this.chatManager = null;
		this.eventManager = null;
	}

	async initialize() {
		// Initialize map
		this.mapManager = new MapManager();
		this.mapManager.initializeMap();

		// Initialize chat
		this.chatManager = new ChatManager(this.mapManager);
		this.chatManager.initialize();

		// Initialize events
		this.eventManager = new EventManager(this.mapManager, this.chatManager);
		this.eventManager.initialize();

		console.log("Climate Viewer App initialized successfully");
	}
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", async () => {
	const app = new ClimateViewerApp();
	await app.initialize();
});

// Export for potential external use
export { ClimateViewerApp };
