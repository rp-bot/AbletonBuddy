"""
Configuration for Ableton Buddy application.
Configures Marvin's database for thread persistence.
"""

import marvin.settings
from marvin.database import ensure_db_tables_exist

# Configure SQLite database for thread persistence
# This enables automatic persistence of threads and messages
marvin.settings.database_url = "sqlite+aiosqlite:///./ableton_buddy.db"

# Initialize database tables on startup
ensure_db_tables_exist()
