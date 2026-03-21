import json
from typing import List
from ai.context_manager import ContextManager
from models.chat import ChatContext, ChatResponse, MapActions, MapState, RAGResponse
from service.ai_service import AIService, OpenAIService
from ai.rag_query_system import ClimateRAGSystem


class ClimateAgent:
    """Single Climate Agent Handling Climate Queries"""

    def __init__(self, ai_service: AIService | None = None):
        # TODO: Allow other AI services to be used
        self.ai_service = ai_service or OpenAIService()
        self.context_manager = ContextManager()
        self.rag_system = ClimateRAGSystem()


    async def process_query(self, query: str, map_state: MapState, session_id: str) -> ChatResponse:
        """Main Entry Point - Handle all queries"""
        context = await self.context_manager.get_context(session_id)
        rag_response = self.rag_system.generate_response(query=query, context=context, map_state=map_state)
        detected_layers = rag_response.metadata.auto_detected_layers
        map_actions = self._generate_map_actions(query, context, map_state, detected_layers, rag_response)
        await self.context_manager.update_context(session_id, query, rag_response.response)
        return ChatResponse(response=rag_response.response, map_actions=[action.model_dump() for action in map_actions])

    def _generate_map_actions(self, query: str, context: ChatContext, map_state: MapState, detected_layers: list[str] | None, rag_response: RAGResponse) -> List[MapActions]:
        """Generate map actions based on RAG response"""
        prompt = self._build_map_actions_prompt(query, context, map_state, detected_layers, rag_response)
        map_action_response = self.ai_service.get_response(prompt=prompt)
        if map_action_response:
          try:
            content = map_action_response.choices[0].message.content or "{}"
            parsed_response = json.loads(content)
            map_actions = parsed_response.get("map_actions", [])
            return [MapActions(**action) for action in map_actions]
          except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return []
        return []


    def _build_map_actions_prompt(
        self, query: str, context: ChatContext, map_state: MapState, detected_layers: list[str] | None, rag_response: RAGResponse
    ) -> str:
        """Build the map actions prompt"""
        response_info = f"Response: {rag_response.response}"

        sw = map_state.map_position.southwest
        ne = map_state.map_position.northeast
        center_lat = (sw.lat + ne.lat) / 2
        center_long = (sw.lng + ne.lng) / 2

        bounds_info = (
            f"Map Position Bounds:\n"
            f"        Southwest: {sw.lat}, {sw.lng}\n"
            f"        Northeast: {ne.lat}, {ne.lng}"
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

        if map_state.available_layers and map_state.available_layers.increment:
          increment_layers_info = "AVAILABLE INCREMENTAL FLOODING LAYERS (use specific foot levels):\n"
          for layer in map_state.available_layers.increment:
            increment_layers_info += f"- {layer}\n"
        else:
          increment_layers_info = "NO AVAILABLE INCREMENTAL FLOODING LAYERS."

        if map_state.available_layers and map_state.available_layers.normal:
          available_normal_layers_info = "AVAILABLE NORMAL LAYERS (do not use foot levels):\n"
          for layer in map_state.available_layers.normal:
            available_normal_layers_info += f"- {layer}\n"
        else:
          available_normal_layers_info = "NO AVAILABLE NORMAL LAYERS."

        return f"""
You are a Hawaiian climate data assistant. Analyze the user's query and provide helpful responses with appropriate map actions.

RAG RESPONSE:
{response_info}

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
    "layer_name": "layer_name",
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

7. SET_FOOT_INCREMENT - Set foot increment
{{
  "type": "set_foot_increment",
  "parameters": {{
    "foot_increment": 4,
    "reason": "Why changing the foot increment"
  }}
}}

{increment_layers_info}

{available_normal_layers_info}

SPECIFIC LOCATIONS:
- Koolaupoko: {{"southwest": [21.25, -157.9], "northeast": [21.35, -157.7]}}
- Waikiki: {{"southwest": [21.26, -157.83], "northeast": [21.28, -157.81]}}

COORDINATE VALIDATION:
- Hawaii bounds: Southwest: [22.5, -154.0], Northeast: [18.5, -161.0]
- Ensure all coordinates fall within these bounds

CRITICAL RULES:
1. Return ONLY valid JSON - no markdown formatting, no code blocks, no extra text
2. Include 1-4 actions maximum per response
3. Only return map_actions, no response text needed
4. Use exact layer names from the available list
5. Validate coordinates are within Hawaii bounds
6. Provide clear reasons for each action"""
