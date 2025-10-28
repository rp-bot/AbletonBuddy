#!/usr/bin/env python3
"""
Run the Ableton Buddy FastAPI server.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if __name__ == "__main__":
    # Import config first to set up environment variables and database
    import config  # noqa: F401

    import uvicorn
    from api import app

    print("🎵 Starting Ableton Buddy API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server\n")

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
