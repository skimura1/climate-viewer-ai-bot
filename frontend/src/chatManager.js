// Chat management module
export class ChatManager {
	constructor(mapManager, mapStateManager) {
		this.mapManager = mapManager;
		this.mapStateManager = mapStateManager;
	}

	initialize() {
		const chatInput = document.getElementById("chat-input");
		const sendBtn = document.getElementById("send-btn");
		const chatMessages = document.getElementById("chat-messages");

		// Auto-resize chat messages container
		this.resizeChatMessages();
		window.addEventListener("resize", () => this.resizeChatMessages());

		this.initializeEventListeners();
	}

	initializeEventListeners() {
		const chatInput = document.getElementById("chat-input");
		const sendBtn = document.getElementById("send-btn");
		const quickActionBtns = document.querySelectorAll(".quick-action-btn");

		// Send message on Enter key
		chatInput.addEventListener("keypress", (e) => {
			if (e.key === "Enter" && !e.shiftKey) {
				e.preventDefault();
				this.sendMessage();
			}
		});

		// Send message on button click
		sendBtn.addEventListener("click", () => this.sendMessage());

		// Quick action buttons
		quickActionBtns.forEach((btn) => {
			btn.addEventListener("click", () => {
				const prompt = btn.getAttribute("data-prompt");
				chatInput.value = prompt;
				this.sendMessage();
			});
		});
	}

	resizeChatMessages() {
		const chatMessages = document.getElementById("chat-messages");
		const headerHeight = document.querySelector(".chatbot-header").offsetHeight;
		const inputHeight = document.querySelector(
			".chat-input-container",
		).offsetHeight;
		const containerHeight =
			document.querySelector(".chatbot-container").offsetHeight;
		chatMessages.style.maxHeight = `${containerHeight - headerHeight - inputHeight - 40}px`;
	}

	sendMessage() {
		const chatInput = document.getElementById("chat-input");
		const message = chatInput.value.trim();

		if (message) {
			this.addUserMessage(message);
			this.sendChatMessage(message);
			chatInput.value = "";
		}
	}

	addUserMessage(message) {
		const chatMessages = document.getElementById("chat-messages");
		const messageDiv = document.createElement("div");
		messageDiv.className = "message user-message";
		messageDiv.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-user"></i>
      </div>
      <div class="message-content">
        <p>${this.escapeHtml(message)}</p>
      </div>
    `;
		chatMessages.appendChild(messageDiv);
		this.scrollToBottom();
	}

	addBotMessage(message) {
		const chatMessages = document.getElementById("chat-messages");
		const messageDiv = document.createElement("div");
		messageDiv.className = "message bot-message";
		messageDiv.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-robot"></i>
      </div>
      <div class="message-content">
        <p>${this.escapeHtml(message)}</p>
      </div>
    `;
		chatMessages.appendChild(messageDiv);
		this.scrollToBottom();
	}

	async sendChatMessage(message) {
		this.showLoading(true);

		try {
			const activeLayers = this.mapManager.getActiveLayers();
			const footIncrement = this.mapManager.getFootIncrement();
			const currentMapPosition = this.mapManager.getCurrentMapBounds();
			const currentZoom = this.mapManager.getCurrentZoom();

			const mapState = {
				active_layers: Array.from(activeLayers),
				foot_increment: footIncrement,
				map_position: currentMapPosition,
				zoom_level: currentZoom,
			};

			const response = await this.getAIResponse(message, mapState);
			const data = response.data;
			const boundaries = data.boundaries;
			const bounds = L.latLngBounds(
				[boundaries.south, boundaries.west], // Southwest
				[boundaries.north, boundaries.east], // Northeast
			);

			const overlayLayers = this.mapManager.getOverlayLayers();
			overlayLayers[data.layer].addTo(this.mapManager.getMap());
			this.mapManager.getMap().fitBounds(bounds);

			this.addBotMessage(data.reason);
		} catch (error) {
			this.addBotMessage(
				"I'm sorry, I'm having trouble processing your request right now. Please try again later.",
			);
			console.error("Chat error:", error);
		} finally {
			this.showLoading(false);
		}
	}

	async getAIResponse(prompt, map_state) {
		const url = "http://127.0.0.1:8000/chat";
		const fetchData = {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ query: prompt, map_state: map_state }),
		};

		try {
			const response = await fetch(url, fetchData);

			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const jsonData = await response.json();
			return jsonData;
		} catch (error) {
			console.log(error);
			return null;
		}
	}

	scrollToBottom() {
		const chatMessages = document.getElementById("chat-messages");
		chatMessages.scrollTop = chatMessages.scrollHeight;
	}

	showLoading(show) {
		const loadingOverlay = document.getElementById("loading-overlay");
		if (show) {
			loadingOverlay.classList.remove("hidden");
		} else {
			loadingOverlay.classList.add("hidden");
		}
	}

	escapeHtml(text) {
		const div = document.createElement("div");
		div.textContent = text;
		return div.innerHTML;
	}
}
