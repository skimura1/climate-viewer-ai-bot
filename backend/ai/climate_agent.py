from context_manager import ContextManager
from backend.service.open_ai_service import OpenAIService
from backend.models.chat import ChatContext

"""Single Climate Agent Handling Climate Queries"""


class ClimateAgent:
    def __init__(self):
        self.openai_service = OpenAIService()
        # self.geoserver_service = GeoserverService()
        self.context_manager = ContextManager()
        self.data_catalog = DataCatalog()

    async def process_query(self, query: str, session_id: str) -> Response:
        """Main Entry Point - Handle all queries"""

        # Get Context
        context = self.context_manager.get_context(session_id)

        # Get Response from AI service
        response = await self._generate_response(query, context)

        # Extract actions from prompt and execute the actions
        # TODO: Figure out what types of actions need to be done
        # actions = self._parse_actions(response)
        # result = await self._execute_actions(actions)

        await self.context_manager.update_context(session_id, query, response)
        return self._format_response(response)

    async def _generate_response(self, query: str, context: ChatContext) -> str:
        """Generate response using single comprehensive prompt"""
        prompt = self._build_comprehensive_prompt(query, context)
        return self.openai_service.get_response(prompt)

    def _build_comprehensive_prompt(self, query: str, context: ChatContext) -> str:
        """Build Single Prompt for all functionality"""
        return f"""
        You are a Hawaiian climate data assistant. Handle this query: "{query}"
        
        Current context:
        - Map bounds: {context.map_bounds}
        - Active layers: {context.active_layers}
        - Available datasets: {self.data_catalog.get_available_datasets()}
        
        Capabilities you can use:
        1. DATA_DISCOVERY: Find and suggest climate datasets
        2. MAP_NAVIGATION: Change map view or zoom
        3. LAYER_MANAGEMENT: Add/remove map layers
        4. DATA_ANALYSIS: Provide simple statistics and summaries
        5. OUT_OF_SCOPE: Politely redirect non-climate queries
        
        Response format:
        {{
            "response_text": "Natural language response to user",
            "actions": [
                {{"type": "add_layer", "layer": "temperature", "region": "oahu"}},
                {{"type": "zoom_to", "location": "honolulu"}},
                {{"type": "analyze_data", "metric": "average_rainfall"}}
            ],
            "suggestions": ["Follow-up question 1", "Follow-up question 2"]
        }}
        """

    def _format_response(self, response: str) -> ChatResponse:
        return f"""
            {
            "layer": "CRC:HI_Oahu_inundation_06ft", 
            "foot_increment": "6", 
            "boundaries": {
                "north": 21.6500, 
                "south": 21.3090, 
                "east": -157.6500, 
                "west": -157.9000
                },
            "reason": "Oahu-specific flooding data at 6 foot level"
            }
        """
