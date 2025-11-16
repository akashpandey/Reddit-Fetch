#!/usr/bin/env python3
"""
Reddit Credentials Validator
This script helps diagnose authentication issues with Reddit API credentials.
"""

import os
import sys
import base64
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def main():
    # Load environment variables
    load_dotenv()

    # Get credentials with whitespace stripped
    client_id = os.getenv("CLIENT_ID", "").strip()
    client_secret = os.getenv("CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv("REDIRECT_URI", "").strip()
    user_agent = os.getenv("USER_AGENT", "").strip()
    reddit_username = os.getenv("REDDIT_USERNAME", "").strip()

    console.print("\n[bold cyan]Reddit Credentials Validator[/bold cyan]\n")

    # Create validation table
    table = Table(title="Credential Check")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Value (first/last 4 chars)", style="green")
    table.add_column("Length", style="yellow")
    table.add_column("Issues", style="red")

    # Validate CLIENT_ID
    client_id_issues = []
    if not client_id:
        client_id_issues.append("MISSING")
    else:
        if len(client_id) < 10:
            client_id_issues.append("Too short")
        if " " in client_id:
            client_id_issues.append("Contains spaces")
        if client_id != client_id.strip():
            client_id_issues.append("Has leading/trailing whitespace")

    table.add_row(
        "CLIENT_ID",
        "✅" if not client_id_issues else "❌",
        f"{client_id[:4]}...{client_id[-4:]}" if len(client_id) > 8 else client_id if client_id else "N/A",
        str(len(client_id)) if client_id else "0",
        ", ".join(client_id_issues) if client_id_issues else "OK"
    )

    # Validate CLIENT_SECRET
    client_secret_issues = []
    if not client_secret:
        client_secret_issues.append("MISSING")
    else:
        if len(client_secret) < 10:
            client_secret_issues.append("Too short")
        if " " in client_secret:
            client_secret_issues.append("Contains spaces")
        if client_secret != client_secret.strip():
            client_secret_issues.append("Has leading/trailing whitespace")

    table.add_row(
        "CLIENT_SECRET",
        "✅" if not client_secret_issues else "❌",
        f"{client_secret[:4]}...{client_secret[-4:]}" if len(client_secret) > 8 else "***" if client_secret else "N/A",
        str(len(client_secret)) if client_secret else "0",
        ", ".join(client_secret_issues) if client_secret_issues else "OK"
    )

    # Validate REDIRECT_URI
    redirect_uri_issues = []
    if not redirect_uri:
        redirect_uri_issues.append("MISSING")
    else:
        if not redirect_uri.startswith(("http://", "https://")):
            redirect_uri_issues.append("Invalid format")
        if " " in redirect_uri:
            redirect_uri_issues.append("Contains spaces")

    table.add_row(
        "REDIRECT_URI",
        "✅" if not redirect_uri_issues else "❌",
        redirect_uri if redirect_uri else "N/A",
        str(len(redirect_uri)) if redirect_uri else "0",
        ", ".join(redirect_uri_issues) if redirect_uri_issues else "OK"
    )

    # Validate USER_AGENT
    user_agent_issues = []
    if not user_agent:
        user_agent_issues.append("MISSING")
    else:
        if len(user_agent) < 5:
            user_agent_issues.append("Too short")
        if not any(char in user_agent for char in ['/', ' ']):
            user_agent_issues.append("Should follow format: AppName/Version by /u/username")

    table.add_row(
        "USER_AGENT",
        "✅" if not user_agent_issues else "❌",
        user_agent if user_agent else "N/A",
        str(len(user_agent)) if user_agent else "0",
        ", ".join(user_agent_issues) if user_agent_issues else "OK"
    )

    # Validate REDDIT_USERNAME
    username_issues = []
    if not reddit_username:
        username_issues.append("MISSING")

    table.add_row(
        "REDDIT_USERNAME",
        "✅" if not username_issues else "❌",
        reddit_username if reddit_username else "N/A",
        str(len(reddit_username)) if reddit_username else "0",
        ", ".join(username_issues) if username_issues else "OK"
    )

    console.print(table)

    # Test credentials with Reddit API
    if client_id and client_secret and not (client_id_issues or client_secret_issues):
        console.print("\n[bold yellow]Testing credentials with Reddit API...[/bold yellow]")

        try:
            # Try to get an app-only access token (doesn't require user authorization)
            auth_string = f"{client_id}:{client_secret}"
            b64_auth = base64.b64encode(auth_string.encode()).decode()

            headers = {
                "Authorization": f"Basic {b64_auth}",
                "User-Agent": user_agent if user_agent else "CredentialValidator/1.0",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {
                "grant_type": "client_credentials"
            }

            console.print("Sending request to Reddit API...")
            response = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                headers=headers,
                data=data,
                timeout=10
            )

            console.print(f"\n[bold]Response Status Code:[/bold] {response.status_code}")
            console.print(f"[bold]Response Headers:[/bold] {dict(response.headers)}\n")

            if response.status_code == 200:
                console.print(Panel.fit(
                    "[bold green]✅ SUCCESS![/bold green]\n\n"
                    "Your CLIENT_ID and CLIENT_SECRET are valid!\n"
                    "Reddit API accepted your credentials.",
                    title="Authentication Test Result",
                    border_style="green"
                ))
                result = response.json()
                console.print(f"\n[dim]Access token received: {result.get('access_token', '')[:20]}...[/dim]")
            elif response.status_code == 401:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                console.print(Panel.fit(
                    f"[bold red]❌ AUTHENTICATION FAILED[/bold red]\n\n"
                    f"Status: {response.status_code}\n"
                    f"Error: {error_data.get('error', 'Unknown')}\n"
                    f"Message: {error_data.get('message', response.text)}\n\n"
                    f"[yellow]Common causes:[/yellow]\n"
                    f"1. CLIENT_ID is incorrect (should be the ID under your app name, NOT the secret)\n"
                    f"2. CLIENT_SECRET is incorrect\n"
                    f"3. Credentials have extra whitespace\n"
                    f"4. App type mismatch (must be 'web app', NOT 'script')\n\n"
                    f"[cyan]Full Response:[/cyan]\n{response.text}",
                    title="Authentication Test Result",
                    border_style="red"
                ))
            else:
                console.print(Panel.fit(
                    f"[bold yellow]⚠️ UNEXPECTED RESPONSE[/bold yellow]\n\n"
                    f"Status: {response.status_code}\n"
                    f"Response: {response.text}",
                    title="Authentication Test Result",
                    border_style="yellow"
                ))

        except requests.exceptions.RequestException as e:
            console.print(Panel.fit(
                f"[bold red]❌ NETWORK ERROR[/bold red]\n\n"
                f"Could not connect to Reddit API:\n{str(e)}",
                title="Connection Test Result",
                border_style="red"
            ))
        except Exception as e:
            console.print(Panel.fit(
                f"[bold red]❌ ERROR[/bold red]\n\n{str(e)}",
                title="Test Result",
                border_style="red"
            ))
    else:
        console.print("\n[bold red]⚠️ Cannot test credentials - please fix the issues above first.[/bold red]")

    # Print helpful instructions
    console.print("\n[bold cyan]How to find your credentials:[/bold cyan]")
    console.print("1. Go to: https://www.reddit.com/prefs/apps")
    console.print("2. Find your app or create a new one (type MUST be: 'web app')")
    console.print("3. CLIENT_ID: The string under your app name (14-22 characters)")
    console.print("4. CLIENT_SECRET: Click 'edit' to see the secret")
    console.print("5. REDIRECT_URI: Must EXACTLY match what you entered in Reddit app settings")
    console.print("\n[dim]Tip: The CLIENT_ID is NOT the same as the CLIENT_SECRET![/dim]\n")

if __name__ == "__main__":
    main()
