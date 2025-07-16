from app import create_app
import os

app = create_app(os.getenv("FLASK_ENV", "development"))


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 8000)),
        debug=bool(os.getenv("FLASK_DEBUG", False)),
    )
