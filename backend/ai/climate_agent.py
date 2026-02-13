import json
from typing import List
from ai.context_manager import ContextManager
from models.chat import ChatContext, ChatResponse, MapActions, MapState
from service.open_ai_service import OpenAIService
from ai.rag_query_system import ClimateRAGSystem


class ClimateAgent:
    """Single Climate Agent Handling Climate Queries"""

    def __init__(self):
        self.openai_service = OpenAIService()
        self.context_manager = ContextManager()
        self.rag_system = ClimateRAGSystem()


    async def process_query(self, query: str, map_state: MapState, session_id: str) -> ChatResponse:
        """Main Entry Point - Handle all queries"""
        context = await self.context_manager.get_context(session_id)
        rag_response = self.rag_system.generate_response(query=query, context=context, map_state=map_state)
        detected_layers = rag_response.metadata.auto_detected_layers
        map_actions = self._generate_map_actions(query, context, map_state, detected_layers)
        await self.context_manager.update_context(session_id, query, rag_response.response)
        return ChatResponse(response=rag_response.response, map_actions=[action.model_dump() for action in map_actions])

    def _generate_map_actions(self, query: str, context: ChatContext, map_state: MapState, detected_layers: list[str] | None) -> List[MapActions]:
        """Generate map actions based on detected layers"""
        if not detected_layers:
          return []
        prompt = self._build_map_actions_prompt(query, context, map_state, detected_layers)
        map_action_response = self.openai_service.get_response(prompt=prompt)
        if map_action_response:
          try:
            parsed_response = json.loads(map_action_response.choices[0].message.content or "{}")
            map_actions = parsed_response.get("map_actions", [])
            return [MapActions(**action) for action in map_actions]
          except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return []
        return []


    def _build_map_actions_prompt(
        self, query: str, context: ChatContext, map_state: MapState, detected_layers: list[str] | None
    ) -> str:
        sw = map_state.map_position.southwest
        ne = map_state.map_position.northeast
        center_lat = (sw[0] + ne[0]) / 2
        center_long = (sw[1] + ne[1]) / 2

        bounds_info = (
            f"Map Position Bounds:\n"
            f"        Southwest: {sw}\n"
            f"        Northeast: {ne}"
        )

        center_info = f"Map Center: lat: {center_lat:.4f}, long: {center_long:.4f}"

        chat_history = f"Chat History: {context.messages}"

        basemap_info = (
            f"Current Basemap: {map_state.basemap_name}"
            if map_state.basemap_name
            else "No basemap currently selected."
        )

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
{basemap_info}

CONVERSATION CONTEXT:
{chat_history}

DETECTED LAYERS:
{detected_layers}

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
      "southwest": [22.0, -157.0],
      "northeast": [21.0, -158.0]
    }},
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

5. SET_ZOOM_LEVEL - Set zoom level
{{
  "type": "set_zoom_level",
  "parameters": {{
    "zoom_level": 10,
    "reason": "Why setting this zoom level"
  }}
}}

6. CHANGE_BASEMAP - Change basemap
{{
  "type": "change_basemap",
  "parameters": {{
    "basemap_id": "basemap_id",
    "reason": "Why changing the basemap"
  }}
}}

INCREMENTAL FLOODING LAYERS (use specific foot levels):
{map_state.available_layers}

AVAILABLE BASEMAP IDS:
{map_state.available_basemaps}

SPECIFIC LOCATIONS:
- Koolaupoko: {{"southwest": [21.25, -157.9], "northeast": [21.35, -157.7]}}
- Waikiki: {{"southwest": [21.26, -157.83], "northeast": [21.28, -157.81]}}

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
- Hawaii bounds: Southwest: [22.5, -154.0], Northeast: [18.5, -161.0]
- Ensure all coordinates fall within these bounds

CRITICAL RULES:
1. Return ONLY valid JSON - no markdown formatting, no code blocks, no extra text
2. Include 1-4 actions maximum per response
3. Always provide a helpful "response" field explaining your analysis
4. Use exact layer names from the available list
5. Validate coordinates are within Hawaii bounds
6. Provide clear reasons for each action"""

    def _format_response(self, response: str | None) -> ChatResponse:
        """Parse AI response and return structured ChatResponse"""
        if response is None:
            return ChatResponse(response="No response received from AI service", map_actions=None)

        response = response.strip()

        json_start = response.find('{')
        json_end = response.rfind('}') + 1

        if json_start != -1 and json_end > json_start:
            json_content = response[json_start:json_end]
        else:
            json_content = response

        try:
            parsed = json.loads(json_content)

            if not isinstance(parsed, dict):
                raise ValueError("Response must be a JSON object")

            ai_response = parsed.get("response", "")
            map_actions = parsed.get("map_actions", [])

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
            if response:
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
