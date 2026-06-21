"""
Configuration file for Discord Spotify Lyrics Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = "!"

# Spotify Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Genius API Configuration
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

# Bot Configuration
UPDATE_INTERVAL = 1  # minutes
LYRICS_CHUNK_SIZE = 1900  # Discord message character limit

# Colors
COLOR_SUCCESS = 0x2ecc71  # Green
COLOR_ERROR = 0xe74c3c   # Red
COLOR_INFO = 0x3498db    # Blue
COLOR_SPOTIFY = 0x1db954  # Spotify Green
