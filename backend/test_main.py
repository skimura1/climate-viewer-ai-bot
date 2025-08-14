import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from main import app
from models.chat import ChatRequest, MapState, MapBounds


class TestChatEndpoint:
    """Test cases for the /chat endpoint"""

    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)

    @pytest.fixture
    def sample_chat_request(self):
        """Sample chat request for testing"""
        return {
            "query": "Show me flooding data for Koolaupoko",
            "map_state": {
                "active_layers": ["flooding_passive_gwi_03ft"],
                "available_layers": ["flooding_passive_gwi_01ft", "flooding_gwi_03ft", "flooding_gwi_05ft"],
                "foot_increment": "100",
                "map_position": {
                    "north": 21.35,
                    "south": 21.25,
                    "east": -157.7,
                    "west": -157.9
                },
                "zoom_level": 10
            }
        }

    @pytest.fixture
    def mock_climate_agent_response(self):
        """Mock response from ClimateAgent"""
        mock_response = Mock()
        mock_response.response = "I'll show you flooding data for Koolaupoko and add the appropriate layers."
        mock_response.map_actions = [
            {
                "type": "add_layer",
                "parameters": {
                    "layer_name": "flooding_passive_gwi_03ft",
                    "display_name": "3ft Groundwater Inundation",
                    "reason": "To show current flooding levels in Koolaupoko"
                }
            },
            {
                "type": "set_bounds",
                "parameters": {
                    "bounds": {
                        "north": 21.35,
                        "south": 21.25,
                        "east": -157.7,
                        "west": -157.9
                    },
                    "zoom_level": 12,
                    "reason": "Focus on Koolaupoko region"
                }
            }
        ]
        return mock_response

    @patch('main.get_climate_agent')
    def test_chat_endpoint_success(self, mock_get_agent, client, sample_chat_request, mock_climate_agent_response):
        """Test successful chat endpoint call"""
        # Mock the climate agent
        mock_agent = Mock()
        mock_agent.process_query = AsyncMock(return_value=mock_climate_agent_response)
        mock_get_agent.return_value = mock_agent

        # Make the request
        response = client.post("/chat", json=sample_chat_request)

        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert "response" in data
        assert "map_actions" in data
        assert len(data["map_actions"]) == 2
        assert data["map_actions"][0]["type"] == "add_layer"
        assert data["map_actions"][1]["type"] == "set_bounds"

    @patch('main.get_climate_agent')
    def test_chat_endpoint_with_invalid_json(self, mock_get_agent, client):
        """Test chat endpoint with invalid JSON"""
        # Mock the climate agent to raise an exception
        mock_agent = Mock()
        mock_agent.process_query = AsyncMock(side_effect=Exception("Test error"))
        mock_get_agent.return_value = mock_agent

        # Make the request
        response = client.post("/chat", json={"invalid": "data"})

        # Should return 500 error
        assert response.status_code == 500
        data = response.json()
        assert "errors" in data

    def test_chat_endpoint_with_missing_fields(self, client):
        """Test chat endpoint with missing required fields"""
        # Missing map_state
        invalid_request = {
            "query": "Test query"
            # Missing map_state
        }

        response = client.post("/chat", json=invalid_request)

        # Should return validation error
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_with_invalid_map_bounds(self, client):
        """Test chat endpoint with invalid map bounds"""
        invalid_request = {
            "query": "Test query",
            "map_state": {
                "active_layers": [],
                "available_layers": [],
                "foot_increment": "100",
                "map_position": {
                    "north": "invalid",  # Should be number
                    "south": 21.25,
                    "east": -157.7,
                    "west": -157.9
                },
                "zoom_level": 10
            }
        }

        response = client.post("/chat", json=invalid_request)

        # Should return validation error
        assert response.status_code == 422

    @patch('main.get_climate_agent')
    def test_chat_endpoint_climate_agent_error(self, mock_get_agent, client, sample_chat_request):
        """Test chat endpoint when ClimateAgent raises an error"""
        # Mock the climate agent to raise an exception
        mock_agent = Mock()
        mock_agent.process_query = AsyncMock(side_effect=Exception("Climate agent error"))
        mock_get_agent.return_value = mock_agent

        # Make the request
        response = client.post("/chat", json=sample_chat_request)

        # Should return 500 error
        assert response.status_code == 500
        data = response.json()
        assert "errors" in data
        assert "Climate agent error" in data["errors"]

    def test_chat_endpoint_cors_headers(self, client, sample_chat_request):
        """Test that CORS headers are properly set"""
        # Mock the climate agent
        with patch('main.get_climate_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.process_query = AsyncMock(return_value=Mock())
            mock_get_agent.return_value = mock_agent

            # Make the request
            response = client.post("/chat", json=sample_chat_request)

            # Check CORS headers
            assert "access-control-allow-origin" in response.headers
            assert "access-control-allow-credentials" in response.headers


class TestRootEndpoint:
    """Test cases for the root endpoint"""

    @pytest.fixture
    def client(self):
        """Test client for FastAPI app"""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello World"


class TestMapStateValidation:
    """Test cases for MapState model validation"""

    def test_valid_map_state(self):
        """Test valid MapState creation"""
        map_state = MapState(
            active_layers=["layer1", "layer2"],
            available_layers=["layer1", "layer2", "layer3"],
            foot_increment="100",
            map_position=MapBounds(north=21.35, south=21.25, east=-157.7, west=-157.9),
            zoom_level=10
        )
        
        assert len(map_state.active_layers) == 2
        assert len(map_state.available_layers) == 3
        assert map_state.foot_increment == "100"
        assert map_state.zoom_level == 10

    def test_map_state_with_empty_layers(self):
        """Test MapState with empty layer lists"""
        map_state = MapState(
            active_layers=[],
            available_layers=[],
            foot_increment="50",
            map_position=MapBounds(north=22.0, south=21.0, east=-157.0, west=-158.0),
            zoom_level=8
        )
        
        assert len(map_state.active_layers) == 0
        assert len(map_state.available_layers) == 0

    def test_map_state_with_none_layers(self):
        """Test MapState with None layer lists"""
        map_state = MapState(
            active_layers=None,
            available_layers=None,
            foot_increment="200",
            map_position=MapBounds(north=22.5, south=18.5, east=-154.0, west=-161.0),
            zoom_level=5
        )
        
        assert map_state.active_layers is None
        assert map_state.available_layers is None


if __name__ == "__main__":
    pytest.main([__file__])
