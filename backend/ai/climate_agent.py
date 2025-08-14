import json

from ai.context_manager import ContextManager
from models.chat import ChatContext, ChatResponse, MapState

# from service.map_service import MapService
from service.open_ai_service import OpenAIService

"""Single Climate Agent Handling Climate Queries"""


class ClimateAgent:
    def __init__(self):
        self.openai_service = OpenAIService()
        # self.geoserver_service = GeoserverService()
        self.context_manager = ContextManager()
        # self.map_service = MapService()
        # self.data_catalog = DataCatalog()  # TODO: Implement DataCatalog

    async def process_query(self, query: str, map_state: MapState, session_id: str) -> ChatResponse:
        """Main Entry Point - Handle all queries"""

        # # Get Context
        # context = await self.context_manager.get_context(
        #     session_id, map_state=self.map_service.get_state()
        # )

        # Get Context
        context = await self.context_manager.get_context(session_id)

        # Get Response from AI service
        response = await self._generate_response(query=query, context=context, map_state=map_state)

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

        #TODO:Something is broken here
        prompt = self._build_comprehensive_prompt(query, context, map_state)
        ai_response = self.openai_service.get_response(prompt=prompt)

        return self._format_response(ai_response.choices[0].message.content)

    def _build_comprehensive_prompt(
        self, query: str, context: ChatContext, map_state: MapState
    ) -> str:
        bounds_info = f"""Map Position Bounds: 
        North: {map_state.map_position.north}
        East: {map_state.map_position.east}
        South: {map_state.map_position.south}
        West: {map_state.map_position.west}"""

        center_info = f"Map Center: lat: {map_state.map_position.north:.4f}," + \
            f"long: {map_state.map_position.east:.4f}"

        chat_history = f"Chat History: {context.messages}"

        if map_state.active_layers:
            layer_info = "Currently displayed layers:\n"
            for layer in map_state.active_layers:
                layer_info += f"- {layer}\n"
        else:
            layer_info = "No data layers currently displayed."

        return f"""
You are a Hawaiian climate data assistant. Analyze the user's query and provide helpful responses with appropriate map actions.

CURRENT MAP STATE:
{bounds_info}
{center_info}
{layer_info}

CONVERSATION CONTEXT:
{chat_history}

USER QUERY: "{query}"

RESPONSE FORMAT:
You MUST respond with valid JSON in this exact structure:

{{
  "response": "Your detailed, helpful response about Hawaiian climate data",
  "map_actions": [
    {{
      "type": "action_type",
      "parameters": {{}}
    }}
  ]
}}

AVAILABLE ACTIONS:

1. ADD_LAYER - Add climate data layer
{{
  "type": "add_layer",
  "parameters": {{
    "layer_name": "exact_layer_identifier",
    "display_name": "Human-readable layer name",
    "reason": "Why this layer helps answer the query"
  }}
}}

2. REMOVE_LAYER - Remove specific layer
{{
  "type": "remove_layer", 
  "parameters": {{
    "layer_name": "layer_to_remove",
    "reason": "Why removing this layer"
  }}
}}

3. SET_BOUNDS - Focus map on geographic area
{{
  "type": "set_bounds",
  "parameters": {{
    "bounds": {{
      "north": 22.0,
      "south": 21.0,
      "east": -157.0,
      "west": -158.0
    }},
    "zoom_level": 10,
    "reason": "Why focusing on this area"
  }}
}}

4. CLEAR_LAYERS - Remove all current layers
{{
  "type": "clear_layers",
  "parameters": {{
    "reason": "Why clearing all layers"
  }}
}}


INCREMENTAL FLOODING LAYERS (use specific foot levels):
${map_state.available_layers}


SPECIFIC LOCATIONS:
- Koolaupoko: {{"north": 21.35, "south": 21.25, "east": -157.7, "west": -157.9}}
- Waikiki: {{"north": 21.28, "south": 21.26, "east": -157.81, "west": -157.83}}

ACTION SELECTION GUIDELINES:
1. For temperature queries: Use temperature_annual or temperature_seasonal
2. For rainfall/drought: Use precipitation layers or drought_severity
3. For flooding/sea level rise: Use specific incremental flooding layers (e.g., flooding_passive_gwi_03ft for 3-foot flooding)
4. For flooding scenarios: Choose appropriate foot level based on user query (0-10ft available)
5. For flooding comparisons: Add multiple specific flood levels (e.g., flooding_passive_gwi_01ft and flooding_passive_gwi_05ft)
6. For specific islands: Set bounds to focus on that island  
7. For comparisons: Add multiple relevant layers with exact names
8. For temporal analysis: Set appropriate time ranges
9. Clear existing layers if starting a new analysis topic
10. Highlight areas when pointing out specific phenomena or risks

FLOODING LAYER SELECTION EXAMPLES:
- "1 foot of flooding" → use "flooding_passive_gwi_01ft"
- "minor flooding" → use "flooding_passive_gwi_01ft" or "flooding_passive_gwi_02ft"
- "moderate flooding" → use "flooding_passive_gwi_03ft" to "flooding_passive_gwi_05ft"
- "severe flooding" → use "flooding_passive_gwi_06ft" to "flooding_passive_gwi_10ft"
- "compare flood levels" → add multiple specific layers like "flooding_passive_gwi_02ft" and "flooding_passive_gwi_06ft"

COORDINATE VALIDATION:
- Hawaii bounds: North: 22.5, South: 18.5, East: -154.0, West: -161.0
- Ensure all coordinates fall within these bounds

CRITICAL RULES:
1. Return ONLY valid JSON - no markdown formatting, no code blocks, no extra text
2. Include 1-4 actions maximum per response
3. Always provide a helpful "response" field explaining your analysis
4. Use exact layer names from the available list
5. Validate coordinates are within Hawaii bounds
6. Provide clear reasons for each action"""

    def _format_response(self, response: str | None) -> ChatResponse:
        """Parse AI response and return structured ChatResponse with improved error handling"""
        if response is None:
            return ChatResponse(response="No response received from AI service", map_actions=None)

        response = response.strip()

        # Try to extract JSON from response if it contains other text
        json_start = response.find('{')
        json_end = response.rfind('}') + 1

        if json_start != -1 and json_end > json_start:
            json_content = response[json_start:json_end]
        else:
            json_content = response

        try:
            parsed = json.loads(json_content)

            # Validate required fields
            if not isinstance(parsed, dict):
                raise ValueError("Response must be a JSON object")

            ai_response = parsed.get("response", "")
            map_actions = parsed.get("map_actions", [])

            # Validate map_actions structure
            if map_actions and isinstance(map_actions, list):
                validated_actions = []
                for action in map_actions:
                    if isinstance(action, dict) and "type" in action:
                        validated_actions.append(action)
                    else:
                        print(f"Warning: Invalid action format: {action}")
                map_actions = validated_actions
            else:
                map_actions = []

            return ChatResponse(
                response=ai_response if ai_response else "I can help with Hawaiian climate data analysis.",
                map_actions=map_actions if map_actions else None
            )

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            # Try to extract meaningful text from the response
            if response:
                # Remove common markdown formatting
                clean_response = response.replace('```json', '').replace('```', '').strip()
                return ChatResponse(
                    response=clean_response if len(clean_response) > 10 else "I encountered an issue processing your request. Could you please rephrase?",
                    map_actions=None
                )
            return ChatResponse(response="Unable to process the request", map_actions=None)

        except (ValueError, KeyError) as e:
            print(f"Response validation error: {e}")
            return ChatResponse(
                response="I had trouble formatting my response. Let me try again with your question.",
                map_actions=None
            )
