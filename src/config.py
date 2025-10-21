"""
Configuration for Ableton Buddy application.
Configures Marvin's database for thread persistence.
"""

import marvin.settings

# Configure SQLite database for thread persistence
# This enables automatic persistence of threads and messages
marvin.settings.database_url = "sqlite:///./ableton_buddy.db"
