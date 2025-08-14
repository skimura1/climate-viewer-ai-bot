# Backend Tests

This directory contains comprehensive tests for the Climate Viewer AI Bot backend that **do not require API tokens**.

## 🚀 Quick Start

### Run All Tests
```bash
cd backend
python run_tests.py
```

### Run Specific Test File
```bash
python run_tests.py test_climate_agent.py
python run_tests.py test_main.py
```

### Run with pytest directly
```bash
pytest test_climate_agent.py -v
pytest test_main.py -v
pytest . -v  # Run all tests
```

## 🧪 Test Coverage

### `test_climate_agent.py`
Tests the core AI logic without making API calls:

- ✅ **ClimateAgent initialization**
- ✅ **Query processing with mocked responses**
- ✅ **JSON response formatting**
- ✅ **Error handling for malformed responses**
- ✅ **Prompt building functionality**
- ✅ **Map action validation**

### `test_main.py`
Tests the FastAPI endpoints with mocked dependencies:

- ✅ **Chat endpoint success cases**
- ✅ **Input validation**
- ✅ **Error handling**
- ✅ **CORS headers**
- ✅ **Model validation**

## 🔧 How It Works

### Mocking Strategy
Instead of calling real APIs, tests use **mocks**:

```python
# Mock OpenAI service to avoid API calls
@patch('main.get_climate_agent')
def test_chat_endpoint_success(self, mock_get_agent, client, sample_chat_request):
    # Mock the climate agent
    mock_agent = Mock()
    mock_agent.process_query = AsyncMock(return_value=mock_response)
    mock_get_agent.return_value = mock_agent
    
    # Test without real API calls
    response = client.post("/chat", json=sample_chat_request)
    assert response.status_code == 201
```

### Sample Data
Tests use realistic sample data:

```python
sample_chat_request = {
    "query": "Show me flooding data for Koolaupoko",
    "map_state": {
        "active_layers": ["flooding_passive_gwi_03ft"],
        "available_layers": ["flooding_passive_gwi_01ft", "flooding_gwi_03ft"],
        "map_position": {
            "north": 21.35, "south": 21.25,
            "east": -157.7, "west": -157.9
        },
        "zoom_level": 10
    }
}
```

## 📋 Test Scenarios

### Happy Path Tests
- ✅ Valid chat requests
- ✅ Proper JSON responses
- ✅ Map action processing
- ✅ State updates

### Error Handling Tests
- ❌ Invalid JSON from AI
- ❌ Malformed responses
- ❌ Missing required fields
- ❌ Invalid map coordinates
- ❌ Climate agent errors

### Edge Cases
- 🔍 Empty layer lists
- 🔍 None values
- 🔍 Boundary conditions
- 🔍 CORS validation

## 🛠️ Adding New Tests

### For New Endpoints
```python
def test_new_endpoint(self, client):
    """Test new endpoint functionality"""
    response = client.get("/new-endpoint")
    assert response.status_code == 200
```

### For New Models
```python
def test_new_model_validation(self):
    """Test new model validation"""
    model = NewModel(field="value")
    assert model.field == "value"
```

### For New Business Logic
```python
@patch('module.dependency')
def test_new_logic(self, mock_dependency):
    """Test new business logic"""
    mock_dependency.return_value = "mocked_value"
    result = new_function()
    assert result == "expected_result"
```

## 🚨 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure you're in the backend directory
cd backend
export PYTHONPATH=.
```

**Missing Dependencies**
```bash
# Install test dependencies
uv sync --group dev
```

**Test Failures**
```bash
# Run with verbose output
pytest -v --tb=long

# Run specific failing test
pytest test_file.py::TestClass::test_method -v
```

## 📊 Test Results

After running tests, you'll see:
- ✅ **Passed tests** with details
- ❌ **Failed tests** with error messages
- 📊 **Summary** of total tests run
- ⏱️ **Execution time**

## 🎯 Benefits

- **No API costs** - Tests run without tokens
- **Fast execution** - No network calls
- **Reliable** - Tests don't depend on external services
- **Comprehensive** - Covers success, error, and edge cases
- **Maintainable** - Easy to add new test scenarios

## 🔄 Continuous Integration

These tests can be easily integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Backend Tests
  run: |
    cd backend
    python run_tests.py
```

Run the tests to verify your backend functionality works correctly without spending API tokens! 🎉
