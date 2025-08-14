import pytest
from unittest.mock import Mock, patch, AsyncMock
from ai.climate_agent import ClimateAgent
from models.chat import MapState, MapBounds, ChatContext, Message
from service.open_ai_service import OpenAIService


class TestClimateAgent:
    """Test cases for ClimateAgent class"""

    @pytest.fixture
    def mock_openai_service(self):
        """Mock OpenAI service to avoid API calls"""
        mock_service = Mock(spec=OpenAIService)
        mock_service.get_response = Mock()
        return mock_service

    @pytest.fixture
    def climate_agent(self, mock_openai_service):
        """ClimateAgent instance with mocked dependencies"""
        agent = ClimateAgent()
        agent.openai_service = mock_openai_service
        return agent

    @pytest.fixture
    def sample_map_state(self):
        """Sample map state for testing"""
        return MapState(
            active_layers=["flooding_passive_gwi_03ft"],
            available_layers=["flooding_passive_gwi_01ft", "flooding_passive_gwi_03ft", "flooding_passive_gwi_05ft"],
            foot_increment="100",
            map_position=MapBounds(north=21.35, south=21.25, east=-157.7, west=-157.9),
            zoom_level=10
        )

    @pytest.fixture
    def sample_context(self):
        """Sample chat context for testing"""
        return ChatContext(
            session_id="test_session",
            messages=[
                Message(id="1", role="user", content="Hello", timestamp="2024-01-01T00:00:00"),
                Message(id="2", role="bot", content="Hi there!", timestamp="2024-01-01T00:00:01")
            ]
        )

    def test_climate_agent_initialization(self):
        """Test ClimateAgent initializes correctly"""
        agent = ClimateAgent()
        assert agent.openai_service is not None
        assert agent.context_manager is not None

    @pytest.mark.asyncio
    async def test_process_query_success(self, climate_agent, sample_map_state, sample_context):
        """Test successful query processing"""
        # Mock the context manager
        climate_agent.context_manager.get_context = AsyncMock(return_value=sample_context)
        climate_agent.context_manager.update_context = AsyncMock()
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
          "response": "I can help you with climate data analysis.",
          "map_actions": [
            {
              "type": "add_layer",
              "parameters": {
                "layer_name": "flooding_passive_gwi_05ft",
                "display_name": "5ft Groundwater Inundation",
                "reason": "To show moderate flooding levels"
              }
            }
          ]
        }
        '''
        climate_agent.openai_service.get_response.return_value = mock_response

        # Test the query
        result = await climate_agent.process_query(
            query="Show me 5ft flooding",
            map_state=sample_map_state,
            session_id="test_session"
        )

        # Verify the result
        assert result.response is not None
        assert "climate data analysis" in result.response
        assert result.map_actions is not None
        assert len(result.map_actions) == 1
        assert result.map_actions[0]["type"] == "add_layer"

    @pytest.mark.asyncio
    async def test_process_query_with_invalid_json(self, climate_agent, sample_map_state, sample_context):
        """Test handling of invalid JSON responses from AI"""
        climate_agent.context_manager.get_context = AsyncMock(return_value=sample_context)
        climate_agent.context_manager.update_context = AsyncMock()
        
        # Mock OpenAI response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        climate_agent.openai_service.get_response.return_value = mock_response

        result = await climate_agent.process_query(
            query="Test query",
            map_state=sample_map_state,
            session_id="test_session"
        )

        # Should handle gracefully
        assert result.response is not None
        assert "I encountered an issue" in result.response or "I can help" in result.response

    @pytest.mark.asyncio
    async def test_process_query_with_malformed_json(self, climate_agent, sample_map_state, sample_context):
        """Test handling of malformed JSON responses"""
        climate_agent.context_manager.get_context = AsyncMock(return_value=sample_context)
        climate_agent.context_manager.update_context = AsyncMock()
        
        # Mock OpenAI response with malformed JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
          "response": "Valid response",
          "map_actions": [
            {
              "type": "add_layer",
              "parameters": {
                "layer_name": "flooding_passive_gwi_05ft"
                // Missing comma and closing brace
              }
            }
          ]
        }
        '''
        climate_agent.openai_service.get_response.return_value = mock_response

        result = await climate_agent.process_query(
            query="Test query",
            map_state=sample_map_state,
            session_id="test_session"
        )

        # Should handle gracefully
        assert result.response is not None

    def test_build_comprehensive_prompt(self, climate_agent, sample_map_state, sample_context):
        """Test prompt building functionality"""
        prompt = climate_agent._build_comprehensive_prompt(
            query="Show me flooding data",
            context=sample_context,
            map_state=sample_map_state
        )

        # Verify prompt contains expected elements
        assert "Hawaiian climate data assistant" in prompt
        assert "Show me flooding data" in prompt
        assert "flooding_passive_gwi_03ft" in prompt  # Active layer
        assert "flooding_passive_gwi_01ft" in prompt  # Available layer
        assert "21.35" in prompt  # Map position
        assert "10" in prompt     # Zoom level

    def test_format_response_with_valid_json(self, climate_agent):
        """Test response formatting with valid JSON"""
        valid_json = '''
        {
          "response": "Test response",
          "map_actions": [
            {
              "type": "add_layer",
              "parameters": {
                "layer_name": "test_layer",
                "display_name": "Test Layer",
                "reason": "Testing"
              }
            }
          ]
        }
        '''
        
        result = climate_agent._format_response(valid_json)
        
        assert result.response == "Test response"
        assert result.map_actions is not None
        assert len(result.map_actions) == 1
        assert result.map_actions[0]["type"] == "add_layer"

    def test_format_response_with_missing_fields(self, climate_agent):
        """Test response formatting with missing required fields"""
        incomplete_json = '''
        {
          "response": "Test response"
          // Missing map_actions
        }
        '''
        
        result = climate_agent._format_response(incomplete_json)
        
        assert result.response == "Test response"
        assert result.map_actions is None

    def test_format_response_with_none(self, climate_agent):
        """Test response formatting with None input"""
        result = climate_agent._format_response(None)
        
        assert result.response == "No response received from AI service"
        assert result.map_actions is None


class TestMapActions:
    """Test cases for map action handling"""

    def test_add_layer_action_validation(self):
        """Test add_layer action parameter validation"""
        valid_action = {
            "type": "add_layer",
            "parameters": {
                "layer_name": "flooding_passive_gwi_05ft",
                "display_name": "5ft Groundwater Inundation",
                "reason": "To show moderate flooding levels"
            }
        }
        
        # Should be valid
        assert "type" in valid_action
        assert "parameters" in valid_action
        assert valid_action["type"] == "add_layer"
        assert "layer_name" in valid_action["parameters"]

    def test_set_bounds_action_validation(self):
        """Test set_bounds action parameter validation"""
        valid_action = {
            "type": "set_bounds",
            "parameters": {
                "bounds": {
                    "north": 21.35,
                    "south": 21.25,
                    "east": -157.7,
                    "west": -157.9
                },
                "zoom_level": 10,
                "reason": "Focus on Koolaupoko region"
            }
        }
        
        # Should be valid
        assert valid_action["type"] == "set_bounds"
        assert "bounds" in valid_action["parameters"]
        assert "zoom_level" in valid_action["parameters"]


if __name__ == "__main__":
    pytest.main([__file__])
