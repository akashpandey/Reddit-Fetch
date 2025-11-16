import os
import sys
import json
import time
import requests
import base64
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from reddit_fetch.config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, USER_AGENT, TOKEN_FILE
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Global variable to store the authorization code
auth_code = None

def is_headless():
    """Detects if the system is running in headless mode."""
    # Manual override via environment variable
    headless_override = os.environ.get("REDDIT_FETCHER_HEADLESS")
    if headless_override is not None:
        return headless_override.lower() in ['1', 'true', 'yes']
    
    # Explicit Docker indicators (high confidence)
    if (os.environ.get("DOCKER") == "1" or 
        os.path.exists("/.dockerenv")):
        return True
    
    # SSH connections (high confidence)
    if (os.environ.get("SSH_CONNECTION") or 
        os.environ.get("SSH_CLIENT")):
        return True
    
    # Check if we can actually open a browser
    try:
        import webbrowser
        browser = webbrowser.get()
        if not browser:
            return True
    except Exception:
        return True
    
    # Platform-specific GUI checks
    if sys.platform.startswith('linux'):
        # On Linux, check for GUI environment more carefully
        display = os.environ.get("DISPLAY")
        xdg_session = os.environ.get("XDG_SESSION_TYPE")
        wayland_display = os.environ.get("WAYLAND_DISPLAY")
        
        # If we have either X11 or Wayland, probably not headless
        if display or wayland_display:
            # But check if it's just a TTY session
            if xdg_session in ['tty', 'console']:
                return True
            return False
        else:
            # No display variables - likely headless
            return True
    
    elif sys.platform == 'darwin':  # macOS
        # macOS usually has GUI unless explicitly headless
        return False
    
    elif sys.platform == 'win32':  # Windows
        # Windows usually has GUI
        return False
    
    # Default: if we can't determine, assume GUI is available
    return False

def is_docker():
    """Detects if running inside Docker container."""
    return (
        os.environ.get("DOCKER") == "1" 
        or os.path.exists("/.dockerenv")
        or os.path.exists("/proc/1/cgroup") and "docker" in open("/proc/1/cgroup").read()
    )

def show_headless_instructions():
    """Shows instructions for headless authentication."""
    authorization_url = (
        f"https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code"
        f"&state=RANDOM_STRING&redirect_uri={REDIRECT_URI}&duration=permanent&scope=identity history read save"
    )
    
    if is_docker():
        # Docker-specific instructions
        console.print(Panel.fit(
            Text.from_markup(
                "[bold red]🐳 DOCKER CONTAINER DETECTED[/bold red]\n\n"
                "[bold yellow]Authentication tokens are required but missing![/bold yellow]\n\n"
                "[white]This Docker container cannot open a web browser for authentication.\n"
                "You need to generate tokens on a system with a web browser.\n\n"
                "[bold cyan]SOLUTION:[/bold cyan]\n"
                "1. On a computer with a web browser, clone this repo\n"
                "2. Install dependencies: [bold]pip install -e .[/bold]\n"
                "3. Create a .env file with your Reddit API credentials\n"
                "4. Run: [bold]python generate_tokens.py[/bold]\n"
                "5. Copy the generated [bold]tokens.json[/bold] to your Docker data directory\n"
                "6. Restart this container\n\n"
                "[dim]For detailed instructions, see the README.md file.[/dim]"
            ),
            title="🔑 Authentication Required",
            border_style="red"
        ))
    else:
        # General headless instructions
        console.print(Panel.fit(
            Text.from_markup(
                "[bold red]🖥️ HEADLESS SYSTEM DETECTED[/bold red]\n\n"
                "[bold yellow]Cannot open web browser for authentication![/bold yellow]\n\n"
                "[white]This system doesn't have a GUI or web browser available.\n"
                "You need to authenticate on a system with a web browser.\n\n"
                "[bold cyan]SOLUTION:[/bold cyan]\n"
                "1. On a computer with a web browser:\n"
                "   • Open this URL in your browser:\n"
                f"   [link]{authorization_url}[/link]\n\n"
                "   • Complete the Reddit authorization\n"
                "   • Copy the authorization code from the redirect URL\n\n"
                "2. Or generate tokens using the browser system:\n"
                "   • Run [bold]python generate_tokens.py[/bold] on browser system\n"
                "   • Copy [bold]tokens.json[/bold] to this headless system\n\n"
                "[bold red]MANUAL AUTHENTICATION URL:[/bold red]\n"
                f"[link]{authorization_url}[/link]\n\n"
                "[dim]For detailed instructions, see the README.md file.[/dim]"
            ),
            title="🔑 Authentication Required",
            border_style="red"
        ))
    
    return None

def load_tokens_safe():
    """Handles token loading safely, ensuring better error handling in headless mode."""
    if not os.path.exists(TOKEN_FILE):
        console.print("❌ [bold red]No authentication tokens found.[/bold red]")
        return None
    
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as file:
            tokens = json.load(file)
        console.print("✅ [bold green]Authentication tokens loaded successfully.[/bold green]")
        return tokens
    except json.JSONDecodeError:
        console.print("❌ [bold red]Token file is corrupted. Please re-authenticate.[/bold red]")
        return None
    except Exception as e:
        console.print(f"❌ [bold red]Error loading tokens: {e}[/bold red]")
        return None

def save_tokens(tokens):
    """Safely saves tokens to `tokens.json`."""
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as file:
            json.dump(tokens, file, indent=2)
        console.print(f"💾 [bold green]Tokens saved to {TOKEN_FILE}[/bold green]")
    except Exception as e:
        console.print(f"❌ [bold red]Error saving tokens: {e}[/bold red]")

def refresh_access_token_safe():
    """Refreshes the access token and handles headless system failures."""
    tokens = load_tokens_safe()
    if not tokens or "refresh_token" not in tokens:
        console.print("❌ [bold red]No refresh token found. Re-authentication required.[/bold red]")
        
        # Check if we're in a headless environment
        if is_headless():
            show_headless_instructions()
            return None
        else:
            # Try to get new tokens on systems with browsers
            return get_new_tokens()

    refresh_token = tokens["refresh_token"]
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post("https://www.reddit.com/api/v1/access_token", 
                               headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            new_token_data = response.json()
            access_token = new_token_data.get("access_token")
            
            if access_token:
                tokens["access_token"] = access_token
                tokens["timestamp"] = time.time()
                
                # Update refresh token if provided
                if "refresh_token" in new_token_data:
                    tokens["refresh_token"] = new_token_data["refresh_token"]
                
                save_tokens(tokens)
                console.print("🔄 [bold green]Access token refreshed successfully.[/bold green]")
                return access_token
            else:
                console.print("❌ [bold red]Invalid access token received from Reddit.[/bold red]")
        else:
            error_detail = ""
            try:
                error_json = response.json()
                error_detail = f"\nError: {error_json.get('error', 'Unknown')}"
                if 'message' in error_json:
                    error_detail += f"\nMessage: {error_json['message']}"
            except:
                error_detail = f"\nResponse: {response.text}"

            console.print(f"❌ [bold red]Failed to refresh access token: {response.status_code}{error_detail}[/bold red]")

            if response.status_code == 401:
                console.print("[yellow]Possible causes:[/yellow]")
                console.print("1. CLIENT_ID or CLIENT_SECRET changed or incorrect")
                console.print("2. Refresh token expired or revoked")
                console.print("3. Credentials have whitespace issues")
    
    except requests.exceptions.RequestException as e:
        console.print(f"❌ [bold red]Network error while refreshing token: {e}[/bold red]")
    except Exception as e:
        console.print(f"❌ [bold red]Unexpected error while refreshing token: {e}[/bold red]")
    
    # Refresh failed - handle based on environment
    if is_headless():
        console.print("❌ [bold red]Token refresh failed in headless environment.[/bold red]")
        show_headless_instructions()
        return None
    else:
        console.print("🔄 [yellow]Token refresh failed, attempting to get new tokens...[/yellow]")
        return get_new_tokens()

def validate_credentials():
    """Validates Reddit API credentials format."""
    issues = []

    if not CLIENT_ID:
        issues.append("CLIENT_ID is missing")
    elif len(CLIENT_ID) < 10:
        issues.append(f"CLIENT_ID seems too short ({len(CLIENT_ID)} chars, expected 14-22)")
    elif " " in CLIENT_ID:
        issues.append("CLIENT_ID contains spaces (this will cause authentication to fail)")

    if not CLIENT_SECRET:
        issues.append("CLIENT_SECRET is missing")
    elif len(CLIENT_SECRET) < 10:
        issues.append(f"CLIENT_SECRET seems too short ({len(CLIENT_SECRET)} chars)")
    elif " " in CLIENT_SECRET:
        issues.append("CLIENT_SECRET contains spaces (this will cause authentication to fail)")

    if not REDIRECT_URI:
        issues.append("REDIRECT_URI is missing")
    elif not REDIRECT_URI.startswith(("http://", "https://")):
        issues.append(f"REDIRECT_URI must start with http:// or https:// (got: {REDIRECT_URI})")

    if not USER_AGENT:
        issues.append("USER_AGENT is missing")
    elif len(USER_AGENT) < 5:
        issues.append("USER_AGENT seems too short")

    if issues:
        console.print("❌ [bold red]Credential validation failed:[/bold red]")
        for issue in issues:
            console.print(f"   • {issue}")
        console.print("\n[cyan]Run 'python validate_credentials.py' for detailed diagnostics[/cyan]")
        return False

    return True

def get_new_tokens():
    """Requests new authentication tokens via OAuth."""
    # Check if we're in a headless environment first
    if is_headless():
        console.print("❌ [bold red]Cannot authenticate in headless environment.[/bold red]")
        show_headless_instructions()
        return None

    global auth_code

    # Validate credentials format
    if not validate_credentials():
        return None
    
    try:
        threading.Thread(target=start_auth_server, daemon=True).start()
        
        authorization_url = (
            f"https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code"
            f"&state=RANDOM_STRING&redirect_uri={REDIRECT_URI}&duration=permanent&scope=identity history read save"
        )

        console.print("🌍 [bold yellow]Opening Reddit authorization page in your browser...[/bold yellow]")
        
        if webbrowser.open(authorization_url):
            console.print("✅ Browser opened successfully")
        else:
            console.print("⚠️ [yellow]Could not open browser automatically.[/yellow]")
            console.print(f"Please manually visit: [link]{authorization_url}[/link]")

        # Wait for authorization code with timeout
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while auth_code is None:
            if time.time() - start_time > timeout:
                console.print("❌ [bold red]Authentication timeout. Please try again.[/bold red]")
                return None
            time.sleep(0.1)

        # Exchange code for tokens
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
        
        response = requests.post(url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            tokens = response.json()
            tokens["timestamp"] = time.time()
            save_tokens(tokens)
            console.print("✅ [bold green]Authentication successful! Tokens saved.[/bold green]")
            return tokens["access_token"]
        else:
            error_detail = ""
            try:
                error_json = response.json()
                error_detail = f"\nError: {error_json.get('error', 'Unknown')}"
                if 'message' in error_json:
                    error_detail += f"\nMessage: {error_json['message']}"
            except:
                error_detail = f"\nResponse: {response.text}"

            console.print(f"❌ [bold red]Authentication failed: {response.status_code}{error_detail}[/bold red]")

            if response.status_code == 401:
                console.print("\n[yellow]Common causes of 401 Unauthorized:[/yellow]")
                console.print("1. CLIENT_ID is incorrect (check it matches your Reddit app)")
                console.print("2. CLIENT_SECRET is incorrect")
                console.print("3. Credentials have leading/trailing whitespace")
                console.print("4. REDIRECT_URI doesn't match your Reddit app settings exactly")
                console.print("\n[cyan]Run 'python validate_credentials.py' to test your credentials[/cyan]")

            return None
            
    except Exception as e:
        console.print(f"❌ [bold red]Authentication error: {e}[/bold red]")
        return None

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query_components = parse_qs(urlparse(self.path).query)
        if "code" in query_components:
            auth_code = query_components["code"][0].strip()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this tab.")
            console.print(f"✅ [bold green]Authorization code received![/bold green]")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: Authorization code not found.")
    
    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass

def start_auth_server():
    """Start a temporary local web server to receive the OAuth callback."""
    try:
        port = int(REDIRECT_URI.split(":")[-1])
        server = HTTPServer(("localhost", port), AuthHandler)
        console.print(f"🌍 [bold blue]Waiting for authorization on {REDIRECT_URI}...[/bold blue]")
        server.handle_request()
    except OSError as e:
        if "Address already in use" in str(e):
            console.print(f"❌ [bold red]Port {REDIRECT_URI.split(':')[-1]} is already in use.[/bold red]")
            console.print("Please close other applications using this port or change REDIRECT_URI.")
        else:
            console.print(f"❌ [bold red]Server error: {e}[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ [bold red]Unexpected server error: {e}[/bold red]")
        sys.exit(1)