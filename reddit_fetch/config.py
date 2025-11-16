import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API credentials - strip whitespace to avoid common issues
CLIENT_ID = os.getenv("CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("REDIRECT_URI", "").strip()  # Must match the Reddit App settings
USER_AGENT = os.getenv("USER_AGENT", "").strip()  # Fetch dynamically
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "").strip()  # Fetch dynamically
TOKEN_FILE = "/data/tokens.json" if os.getenv("DOCKER", "0") == "1" else "tokens.json"

def exponential_backoff(attempt, base_delay=1.0, max_delay=16.0):
    """Implements exponential backoff to avoid rate limiting."""
    delay = min(base_delay * (2 ** attempt), max_delay)
    time.sleep(delay)
