# Climate Viewer AI Bot

A Flask-based REST API for climate 

## Project Structure

```
climate-viewer-ai-bot/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── extensions.py        # Flask extensions
│   ├── api/                 # API Blueprints
│   ├── models/              # Data Models/Schemas
│   └── services/            # Business Logic
├── run.py                   # Application entry point
├── pyproject.toml          # Project dependencies
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd climate-viewer-ai-bot
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using uv:
```bash
uv sync
```

4. Create a `.env` file in the root directory:
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Security
SECRET_KEY=your-secret-key-change-in-production

# API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Logging
LOG_LEVEL=INFO
```

5. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/api/v1/health`
- Returns service health status

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `FLASK_HOST` | Host to bind to | `0.0.0.0` |
| `FLASK_PORT` | Port to bind to | `5000` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `LOG_LEVEL` | Logging level | `INFO` |


## License

This project is licensed under the MIT License.
