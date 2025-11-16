import time
import requests
import base64
import os
import webbrowser
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API Credentials - strip whitespace to avoid common issues
CLIENT_ID = os.getenv("CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("REDIRECT_URI", "").strip()  # Must match the one registered in Reddit App
USER_AGENT = os.getenv("USER_AGENT", "").strip()  # Fetch dynamically
TOKEN_FILE = "tokens.json"

# Global variable to store auth code
auth_code = None

# Step 1: Create a Local Server to Capture Authorization Code
class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query_components = parse_qs(urlparse(self.path).query)
        if "code" in query_components:
            auth_code = query_components["code"][0].strip()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this tab.")
            print(f"✅ Authorization Code Captured: {auth_code}")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: Authorization code not found.")

def start_auth_server():
    """Starts a local HTTP server to capture the Reddit authorization code."""
    server = HTTPServer(("localhost", 8080), AuthHandler)
    print("🌍 Waiting for authorization...")
    server.handle_request()

def load_existing_tokens():
    """Checks if a refresh token is already stored in tokens.json."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as file:
                tokens = json.load(file)
                if "refresh_token" in tokens:
                    print("✅ Refresh token already exists. No need to re-authenticate.")
                    return True  # A refresh token is already stored
        except (json.JSONDecodeError, ValueError):
            print("❌ Token file is corrupted. Re-authenticating...")
    return False  # No valid refresh token found, proceed with OAuth

def get_tokens():
    """Fetch new OAuth tokens from Reddit and store only the refresh token."""
    # Check if refresh token already exists
    if load_existing_tokens():
        return  # Skip authentication

    global auth_code
    threading.Thread(target=start_auth_server, daemon=True).start()

    authorization_url = (
        f"https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code"
        f"&state=RANDOM_STRING&redirect_uri={REDIRECT_URI}&duration=permanent&scope=identity history read save"
    )

    print("🌍 Opening Reddit authorization page in your browser...")
    webbrowser.open(authorization_url)

    while auth_code is None:
        time.sleep(0.1)

    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    
    url = "https://www.reddit.com/api/v1/access_token"
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()

        # Save only the refresh token (no timestamp needed)
        token_data = {"refresh_token": tokens["refresh_token"]}

        with open(TOKEN_FILE, "w", encoding="utf-8") as file:
            json.dump(token_data, file)

        print("✅ Refresh token saved in tokens.json")
    else:
        error_detail = ""
        try:
            error_json = response.json()
            error_detail = f"\nError: {error_json.get('error', 'Unknown')}"
            if 'message' in error_json:
                error_detail += f"\nMessage: {error_json['message']}"
        except:
            error_detail = f"\nResponse: {response.text}"

        print(f"❌ Authentication failed: {response.status_code}{error_detail}")

        if response.status_code == 401:
            print("\n⚠️  Common causes of 401 Unauthorized:")
            print("1. CLIENT_ID is incorrect (should be the ID under your app name)")
            print("2. CLIENT_SECRET is incorrect")
            print("3. Credentials have leading/trailing whitespace")
            print("4. REDIRECT_URI doesn't match your Reddit app settings exactly")
            print("\n💡 Run 'python validate_credentials.py' to test your credentials")

if __name__ == "__main__":
    get_tokens()