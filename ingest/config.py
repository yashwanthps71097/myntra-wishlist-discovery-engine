import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# App Configurations
RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "data/raw")

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Reddit API Credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MyntraWishlistDiscoveryEngine/0.1")

# YouTube API Credentials
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def has_reddit_creds():
    return bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)

def has_youtube_creds():
    return bool(YOUTUBE_API_KEY)
