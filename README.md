
# Reddit Saved Posts Fetcher

Automatically fetch and export your saved Reddit posts and comments to JSON or HTML format.

## Features

* **Incremental Sync** - Only fetches new posts since last run
* **Force Fetch** - Option to re-download all saved posts
* **Multiple Formats** - Export to JSON or HTML bookmarks
* **Docker Support** - Easy containerized deployment
* **Smart Authentication** - Handles token refresh automatically
* **Credential Validator** - Built-in tool to diagnose authentication issues

---

## Prerequisites

### Get Reddit API Credentials

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click **"Create App"** or **"Create Another App"**
3. Fill out the form:
   * **Name** : `My Reddit Fetcher` (or any name)
   * **App type** : Select **"web app"** (NOT "script")
   * **Redirect URI** : `http://localhost:8080`
4. Click **"Create app"**
5. Copy your credentials:
   * **Client ID**: The short string UNDER your app name (14-22 characters, e.g., `DyPeM38zXGcvax`)
   * **Client Secret**: Click "edit" to reveal the longer secret string

**Common mistakes**:
- The CLIENT_ID is the small text under your app name, NOT the secret!
- App type must be "web app" for OAuth to work properly

---

## Usage Methods

Choose one of these three methods:

## Method 1: CLI Script (Local Development)

 **Best for** : Testing, development, one-time use

### Setup

```bash
git clone https://github.com/your-username/Reddit-Fetch.git
cd Reddit-Fetch

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package and dependencies
pip install -e .
```

### Configure

Create a `.env` file:

```ini
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:8080
USER_AGENT=RedditFetcher/1.0 (by /u/your_reddit_username)
REDDIT_USERNAME=your_reddit_username
```

**Important**: Make sure there are no extra spaces or quotes around your credentials!

### Validate Credentials (Recommended)

Before authenticating, test your credentials to avoid common issues:

```bash
python validate_credentials.py
```

This script will:
- Check if all required credentials are present
- Validate credential format
- Test your CLIENT_ID and CLIENT_SECRET with Reddit API
- Show detailed error messages if something is wrong

### Authenticate

```bash
python generate_tokens.py
```

This opens your browser to authorize the app and creates `tokens.json`.

### Run

```bash
# Interactive mode
reddit-fetcher

# Non-interactive mode
OUTPUT_FORMAT=json FORCE_FETCH=false reddit-fetcher
```

---

## Method 2: Build Your Own Docker Image

 **Best for** : Custom modifications, self-hosted environments

### Step 1: Prepare Authentication (on a computer with browser)

```bash
git clone https://github.com/your-username/Reddit-Fetch.git
cd Reddit-Fetch

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package and dependencies
pip install -e .
```

Create `.env` file:

```ini
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:8080
USER_AGENT=RedditFetcher/1.0 (by /u/your_reddit_username)
REDDIT_USERNAME=your_reddit_username
```

**Important**: No extra spaces or quotes around credentials!

Validate credentials (recommended):

```bash
python validate_credentials.py
```

Generate tokens:

```bash
python generate_tokens.py
```

### Step 2: Build Docker Image

```bash
docker build -t reddit-fetcher .
```

### Step 3: Prepare Files for Container

```bash
# Create data directory
mkdir -p ./data

# Copy authentication tokens
cp tokens.json ./data/
```

### Step 4: Run Container

```bash
# One-time run
docker run --rm \
  --env-file .env \
  -e OUTPUT_FORMAT=json \
  -e FORCE_FETCH=false \
  -v $(pwd)/data:/data \
  reddit-fetcher

# Or use docker-compose.yml
docker-compose up -d
```

**docker-compose.yml:**

```yaml
version: '3.8'
services:
  reddit-fetcher:
    build: .  # Builds from local Dockerfile
    container_name: reddit-fetcher
    env_file: .env
    environment:
      - DOCKER=1
      - FETCH_INTERVAL=86400  # Run every 24 hours
      - OUTPUT_FORMAT=json
      - FORCE_FETCH=false
    volumes:
      - ./data:/data
    restart: unless-stopped
```

---

## Method 3: Use Pre-built Docker Image (Recommended)

 **Best for** : Production use, quick deployment, automated scheduling

### Step 1: Prepare Authentication (on a computer with browser)

 **⚠️ Important** : You must do this step on a computer with a web browser first.

```bash
git clone https://github.com/your-username/Reddit-Fetch.git
cd Reddit-Fetch

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package and dependencies
pip install -e .
```

Create `.env` file:

```ini
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:8080
USER_AGENT=RedditFetcher/1.0 (by /u/your_reddit_username)
REDDIT_USERNAME=your_reddit_username
```

**⚠️ Important**: No extra spaces or quotes around credentials!

Validate credentials (recommended):

```bash
python validate_credentials.py
```

Generate authentication tokens:

```bash
python generate_tokens.py
```

### Step 2: Prepare Docker Environment

**Copy files to your Docker server:**

```bash
# Create project directory
mkdir reddit-fetcher-docker
cd reddit-fetcher-docker

# Copy .env file to project directory
cp /path/to/Reddit-Fetch/.env .

# Create data directory and copy tokens
mkdir data
cp /path/to/Reddit-Fetch/tokens.json ./data/
```

### Step 3: Create docker-compose.yml

```yaml
version: '3.8'
services:
  reddit-fetcher:
    image: pandeyak/reddit-fetcher:latest  # Pre-built image from Docker Hub
    container_name: reddit-fetcher
    env_file: .env  # Loads Reddit API credentials
    environment:
      - DOCKER=1
      - FETCH_INTERVAL=86400  # Run every 24 hours (in seconds)
      - OUTPUT_FORMAT=json    # Choose: json or html
      - FORCE_FETCH=false     # Set to true to fetch all posts
    volumes:
      - ./data:/data  # Maps local data directory to container
    restart: unless-stopped
```

### Step 4: Run

```bash
# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### File Structure for Method 3:

```
reddit-fetcher-docker/
├── docker-compose.yml
├── .env                    # Reddit API credentials
└── data/
    ├── tokens.json         # Authentication tokens (copied from Step 1)
    ├── saved_posts.json    # Output file (generated)
    └── last_fetch.json     # Tracking file (generated)
```

---

## Configuration Options

### Environment Variables

| Variable            | Description                          | Default                   | Required |
| ------------------- | ------------------------------------ | ------------------------- | -------- |
| `CLIENT_ID`       | Reddit app client ID                 | -                         | ✅       |
| `CLIENT_SECRET`   | Reddit app client secret             | -                         | ✅       |
| `REDIRECT_URI`    | OAuth redirect URI                   | `http://localhost:8080` | ✅       |
| `USER_AGENT`      | Reddit API user agent                | -                         | ✅       |
| `REDDIT_USERNAME` | Your Reddit username                 | -                         | ✅       |
| `OUTPUT_FORMAT`   | Export format:`json`or `html`    | `json`                  | ❌       |
| `FORCE_FETCH`     | Fetch all posts:`true`or `false` | `false`                 | ❌       |
| `FETCH_INTERVAL`  | Seconds between runs (Docker only)   | `86400`                 | ❌       |

### Docker-specific Commands

```bash
# One-time run with pre-built image
docker run --rm \
  --env-file .env \
  -e OUTPUT_FORMAT=json \
  -e FORCE_FETCH=false \
  -v $(pwd)/data:/data \
  pandeyak/reddit-fetcher:latest

# Force fetch all posts
docker run --rm \
  --env-file .env \
  -e FORCE_FETCH=true \
  -v $(pwd)/data:/data \
  pandeyak/reddit-fetcher:latest
```

---

## Using as Python Library

```python
from reddit_fetch.api import fetch_saved_posts

# Fetch new posts in JSON format
result = fetch_saved_posts(format="json", force_fetch=False)
print(f"Found {result['count']} new posts")

# Access the posts
posts = result['content']
for post in posts:
    print(f"- {post['title']} (r/{post['subreddit']})")
```

---

## Output Files

### JSON Format (`saved_posts.json`)

```json
[
  {
    "title": "Amazing post title",
    "url": "https://reddit.com/r/example/...",
    "subreddit": "example",
    "created_utc": 1649123456,
    "fullname": "t3_abc123",
    "type": "post",
    "author": "username",
    "score": 42
  }
]
```

### HTML Format (`saved_posts.html`)

Beautiful HTML file with styled bookmarks, perfect for importing into bookmark managers.

---

## Troubleshooting

### Authentication Issues

**Error: "Invalid client id" or "401 Unauthorized"**

This is the most common issue! Run the credential validator first:

```bash
python validate_credentials.py
```

**Common causes:**

1. **CLIENT_ID is incorrect**
   - The CLIENT_ID is the string UNDER your app name (14-22 characters)
   - It's NOT the same as CLIENT_SECRET
   - Find it at: https://www.reddit.com/prefs/apps

2. **Extra whitespace in credentials**
   - Remove any quotes, spaces, or line breaks from your .env file
   - Example: `CLIENT_ID=abc123` (NOT `CLIENT_ID= abc123 `)

3. **CLIENT_SECRET is incorrect**
   - Click "edit" on your Reddit app to see the secret
   - Make sure you copied the entire secret

4. **REDIRECT_URI doesn't match**
   - Must EXACTLY match what's in your Reddit app settings
   - Common: `http://localhost:8080` (note: http, not https)

5. **App type mismatch**
   - Your Reddit app MUST be type "web app"
   - If you created a "script" type app, delete it and create a new "web app"

**Error: "No authentication tokens found"**

* **CLI** : Make sure `tokens.json` exists in project directory
* **Docker** : Ensure `tokens.json` is in the `data/` directory
* **Solution** : Regenerate tokens with `python generate_tokens.py`

**Error: "Failed to refresh access token"**

* Delete `tokens.json` and regenerate tokens
* Check that your Reddit app credentials are correct
* Run `python validate_credentials.py` to diagnose

### Docker Issues

**Error: "Cannot open web browser" in Docker**

* This is expected! Docker containers can't open browsers
* You must generate tokens on a computer with a browser first (Step 1)

**Error: "Permission denied" in Docker**

* Fix file permissions: `chmod 644 tokens.json .env`
* Fix directory permissions: `chmod 755 data/`

**Error: "File not found" in Docker**

* Verify file structure matches the example above
* Ensure `.env` and `tokens.json` are in correct locations

### General Issues

**"No new posts found"**

* Check if you have new saved posts on Reddit
* Try force fetch: Set `FORCE_FETCH=true`
* Verify `REDDIT_USERNAME` in `.env` is correct

**"Headless system detected" on desktop**

* Override detection: `REDDIT_FETCHER_HEADLESS=false reddit-fetcher`

---

## Method Comparison

| Feature                   | CLI Script      | Build Docker  | Pre-built Docker |
| ------------------------- | --------------- | ------------- | ---------------- |
| **Setup Time**      | Fast            | Medium        | Fast             |
| **Customization**   | Full            | Full          | Limited          |
| **Dependencies**    | Python required | Docker only   | Docker only      |
| **Auto-scheduling** | Manual/cron     | Built-in      | Built-in         |
| **Updates**         | Git pull        | Rebuild image | Pull new image   |
| **Best for**        | Development     | Custom needs  | Production       |

---

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details.
