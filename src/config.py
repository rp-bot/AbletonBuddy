"""
Configuration for Ableton Buddy application.
Configures Marvin's database for thread persistence.
Loads environment variables from .env file.
"""

import os
from pathlib import Path

# Load .env file if it exists
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(env_file, override=False)
    except ImportError:
        # Fallback: manually parse .env file if python-dotenv not installed
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value

# Import marvin after loading .env file so API keys are available
import marvin.settings  # noqa: E402
from marvin.database import ensure_db_tables_exist  # noqa: E402

# Configure SQLite database for thread persistence
# This enables automatic persistence of threads and messages
marvin.settings.database_url = "sqlite+aiosqlite:///./ableton_buddy.db"

# Initialize database tables on startup
ensure_db_tables_exist()

# Note: Custom thread table will be initialized on first API call
# to avoid asyncio.run() issues during import
