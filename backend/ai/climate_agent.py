import json
from context_manager import ContextManager

from backend.models.chat import ChatContext, MapState, ChatResponse
from backend.service.map_service import MapService
from backend.service.open_ai_service import OpenAIService

"""Single Climate Agent Handling Climate Queries"""


class ClimateAgent:
    def __init__(self):
        self.openai_service = OpenAIService()
        # self.geoserver_service = GeoserverService()
        self.context_manager = ContextManager()
        self.map_service = MapService()
        # self.data_catalog = DataCatalog()  # TODO: Implement DataCatalog

    async def process_query(self, query: str, session_id: str) -> ChatResponse:
        """Main Entry Point - Handle all queries"""

        # # Get Context
        # context = await self.context_manager.get_context(
        #     session_id, map_state=self.map_service.get_state()
        # )

        # Get Context
        context = await self.context_manager.get_context(session_id)

        # Get Response from AI service
        response = await self._generate_response(
            query, context, self.map_service.get_state()
        )

        # Extract actions from prompt and execute the actions
        # TODO: Figure out what types of actions need to be done
        # actions = self._parse_actions(response)
        # result = await self._execute_actions(actions)

        await self.context_manager.update_context(session_id, query, response.response)
        return response

    async def _generate_response(
        self, query: str, context: ChatContext, map_state: MapState
    ) -> ChatResponse:
        """Generate response using single comprehensive prompt"""
        prompt = self._build_comprehensive_prompt(query, context, map_state)
        ai_response = self.openai_service.get_response(prompt=prompt)
        return self._format_response(ai_response.output_text)

    def _build_comprehensive_prompt(
        self, query: str, context: ChatContext, map_state: MapState
    ) -> str:
        bounds_info = f"""
        Chat History: {context.messages}

        Current view bounds: North {map_state.current_map_position.north}, South {map_state.current_map_position.south}, East {map_state.current_map_position.east}, West {map_state.current_map_position.west} at zoom level {map_state.current_map_position.zoom}"""

        center_info = f"""
        Map Center: {map_state.center["lat"]:.4f}, {map_state.center["lng"]:.4f}
        """

        if map_state.active_layers:
            layer_info = "Currently displayed layers:\n"
            for layer in map_state.active_layers:
                layer_info += f"{layer}, "
        else:
            layer_info = "No data layers currently displayed."

        return f"""
CURRENT MAP CONTEXT:
{bounds_info}
{center_info}
{layer_info}

USER QUERY: "{query}"

INSTRUCTIONS:
You are a Hawaiian climate data assistant. Analyze the user's query and choose the most appropriate actions to help them. You can perform multiple actions if needed. Respond with ONLY valid JSON in the exact format below.

REQUIRED JSON FORMAT:
{{
  "response": "Your helpful response about Hawaiian climate data here",
  "map_actions": [
    {{
      "type": "add_layer",
      "layer": {{
        "name": "temperature_annual",
        "display_name": "Annual Temperature"
      }}
    }},
    {{
      "type": "set_bounds",
      "bounds": {{
        "north": 21.8,
        "south": 21.2,
        "east": -157.6,
        "west": -158.3
      }},
      "reason": "Focusing on Oahu for temperature analysis"
    }}
  ]
}}

ACTION TYPES YOU CAN CHOOSE FROM:

1. ADD_LAYER - Add climate data visualization
{{
  "type": "add_layer",
  "layer": {{
    "name": "layer_name",
    "display_name": "Human readable name"
  }}
}}

2. REMOVE_LAYER - Remove existing layer
{{
  "type": "remove_layer",
  "layer_id": "layer_identifier"
}}

3. SET_BOUNDS - Focus map on specific area
{{
  "type": "set_bounds",
  "bounds": {{
    "north": number,
    "south": number,
    "east": number,
    "west": number
  }},
  "reason": "Why focusing on this area"
}}

4. CLEAR_LAYERS - Remove all current layers
{{
  "type": "clear_layers",
  "reason": "Why clearing layers"
}}

5. HIGHLIGHT_AREA - Draw attention to specific region
{{
  "type": "highlight_area",
  "area": {{
    "north": number,
    "south": number,
    "east": number,
    "west": number
  }},
  "style": "highlight|outline|marker",
  "label": "Area description"
}}

AVAILABLE CLIMATE LAYERS:
- Passive GWI [00-10] ft all-scenarios: Statewide 80% probability flooding data (specify ft level 00-10 based on user query)
- Passive SCI [00-10] ft all-scendarios
- Potential Groundwater inundation  [00-10]ft all-scenarios`
- Emergent and Damaging Shallow Groundwater  [00-10]ft all-scenarios
- Drainage backflow [00-10]ft all-scenarios
- Annual wave [00-10]ft all-scenarios
- Kona storm scenario [00-10]ft all-scenarios

ISLAND COORDINATES:
- Waikiki: {{"north": 21.2, "south": 21.3, "east": -157.8, "west": -157.8}}
- Koolaupoko: {{"north": 21.6, "south": 21.3, "east": -157.6, "west": -157.9}}

DECISION GUIDELINES:
- Choose 1-3 actions that best address the user's query
- If comparing data, add multiple relevant layers
- If asking about specific islands, set appropriate bounds
- If starting fresh analysis, consider clearing existing layers first
- Use highlight_area for drawing attention to phenomena or patterns

CRITICAL: Return ONLY the JSON object. No markdown, no additional text.
        """

    def _format_response(self, response: str) -> ChatResponse:
        """Parse AI response and return structured ChatResponse"""
        try:
            # Try to parse JSON response from AI
            parsed = json.loads(response)
            return ChatResponse(
                response=parsed.get("response", response),
                map_actions=parsed.get("map_actions"),
            )
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            return ChatResponse(response=response, map_actions=None)
