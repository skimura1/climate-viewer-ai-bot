// Event management module
export class EventManager {
	constructor(mapManager, chatManager) {
		this.mapManager = mapManager;
		this.chatManager = chatManager;
	}

	initialize() {
		this.initializeMapEvents();
		this.initializeUIEvents();
		this.initializeKeyboardEvents();
	}

	initializeMapEvents() {
		const map = this.mapManager.getMap();

		// Handle map clicks
		map.on("click", (e) => {
			this.handleMapClick(e.latlng);
		});
	}

	initializeUIEvents() {
		const fullscreenBtn = document.getElementById("fullscreen-btn");

		// Fullscreen button
		fullscreenBtn.addEventListener("click", () => {
			this.mapManager.toggleFullscreen();
		});
	}

	initializeKeyboardEvents() {
		// Handle escape key for fullscreen
		document.addEventListener("keydown", (e) => {
			if (e.key === "Escape" && this.mapManager.isFullscreen) {
				this.mapManager.toggleFullscreen();
			}
		});
	}

	async handleMapClick(latlng) {
		// Get location name and handle the click
		const locationName = await this.mapManager.getLocationName(latlng);
		console.log(`Clicked on: ${locationName} at ${latlng.lat}, ${latlng.lng}`);

		// You can add more map click handling logic here
		// For example, adding markers, showing popups, etc.
	}
}

