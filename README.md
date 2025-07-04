# Reddit Saved Posts Fetcher

Automatically fetch and export your saved Reddit posts and comments to JSON or HTML format.

## Features

- **Incremental Sync** - Only fetches new posts since last run
- **Force Fetch** - Option to re-download all saved posts
- **Multiple Formats** - Export to JSON or HTML bookmarks
- **Docker Support** - Easy containerized deployment
- **Smart Authentication** - Handles token refresh automatically

## File Location Summary

Understanding where to place `.env` and `tokens.json` for each method:

### Method 1: CLI Script
```
your-project/               # Git clone directory
├── .env                   # Create here
├── tokens.json            # Generated here
├── saved_posts.json       # Output here
└── reddit_fetch/          # Source code
```

### Method 2: Build Your Own Image
```
# Source directory (for building)
Reddit-Fetch/
├── .env                   # Create here for auth generation
├── tokens.json            # Generated here
└── Dockerfile             # Build from here

# Deployment directory (for running)
reddit-fetcher-deploy/
├── docker-compose.yml
├── .env                   # Copy from source directory
└── data/
    └── tokens.json        # Copy from source directory
```

### Method 3: Pre-built Image
```
# Source directory (any computer with browser)
temp-auth-setup/
├── .env                   # Create here for auth generation
└── tokens.json            # Generated here

# Deployment directory (VPS/server)
reddit-fetcher-docker/
├── docker-compose.yml
├── .env                   # Copy from source directory
└── data/
    └── tokens.json        # Copy from source directory
```

---

## Prerequisites

### Get Reddit API Credentials

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click **"Create App"** or **"Create Another App"**
3. Fill out the form:
   - **Name**: `My Reddit Fetcher` (or any name)
   - **App type**: Select **"web app"**
   - **Redirect URI**: `http://localhost:8080`
4. Click **"Create app"**
5. Copy your **Client ID** (under the app name) and **Client Secret**

---

## Usage Methods

Choose one of these three methods:

## Method 1: CLI Script (Local Development)

**Best for**: Testing, development, one-time use

### Setup
```bash
git clone https://github.com/your-username/Reddit-Fetch.git
cd Reddit-Fetch
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

**Best for**: Custom modifications, self-hosted environments

### Step 1: Prepare Authentication (on a computer with browser)
```bash
git clone https://github.com/your-username/Reddit-Fetch.git
cd Reddit-Fetch
pip install -e .
```

Create `.env` file in the project directory:
```ini
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:8080
USER_AGENT=RedditFetcher/1.0 (by /u/your_reddit_username)
REDDIT_USERNAME=your_reddit_username
```

Generate tokens:
```bash
python generate_tokens.py
```

### Step 2: Build Docker Image
```bash
docker build -t reddit-fetcher .
```

### Step 3: Prepare Files for Docker Deployment

**Important**: The build includes your code, but you need to provide credentials for runtime:

```bash
# Create deployment directory (can be anywhere)
mkdir reddit-fetcher-deploy
cd reddit-fetcher-deploy

# Copy .env file from your source directory
cp /path/to/Reddit-Fetch/.env .

# Create data directory and copy tokens  
mkdir data
cp /path/to/Reddit-Fetch/tokens.json ./data/
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

# Or create docker-compose.yml in your deployment directory
```

**docker-compose.yml for Method 2:**
```yaml
version: '3.8'
services:
  reddit-fetcher:
    image: reddit-fetcher  # Your locally built image
    container_name: reddit-fetcher
    env_file: .env         # Must be in same directory as this file
    environment:
      - DOCKER=1
      - FETCH_INTERVAL=86400  # Run every 24 hours
      - OUTPUT_FORMAT=json
      - FORCE_FETCH=false
    volumes:
      - ./data:/data         # data/ must contain tokens.json
    restart: unless-stopped
```

### File Structure for Method 2:
```
reddit-fetcher-deploy/          # Your deployment directory
├── docker-compose.yml
├── .env                        # Reddit API credentials (copied from source)
└── data/
    ├── tokens.json            # Authentication tokens (copied from source)
    ├── saved_posts.json       # Output file (generated)
    └── last_fetch.json        # Tracking file (generated)
```

---

## Method 3: Use Pre-built Docker Image (Recommended)

**Best for**: Production use, quick deployment, automated scheduling

### Step 1: Prepare Authentication (on a computer with browser)

**⚠️ Important**: You must do this step on a computer with a web browser first.

```bash
git clone https://github.com/your-username/Reddit-Fetch.git
cd Reddit-Fetch
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

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CLIENT_ID` | Reddit app client ID | - | ✅ |
| `CLIENT_SECRET` | Reddit app client secret | - | ✅ |
| `REDIRECT_URI` | OAuth redirect URI | `http://localhost:8080` | ✅ |
| `USER_AGENT` | Reddit API user agent | - | ✅ |
| `REDDIT_USERNAME` | Your Reddit username | - | ✅ |
| `OUTPUT_FORMAT` | Export format: `json` or `html` | `json` | ❌ |
| `FORCE_FETCH` | Fetch all posts: `true` or `false` | `false` | ❌ |
| `FETCH_INTERVAL` | Seconds between runs (Docker only) | `86400` | ❌ |

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

#### HTML Output Preview:
The HTML format creates a clean, Reddit-inspired webpage with your saved posts:

<div style="border: 2px solid #ddd; border-radius: 8px; padding: 10px; background: #f9f9f9; margin: 10px 0;">

**Preview of saved_posts.html:**
![image](https://github.com/user-attachments/assets/e49bbb7f-6aac-4fb7-9262-9d10c04f7da8)
</div>

**Features of HTML output:**
- ✅ **Clean, responsive design** with Reddit's signature orange theme
- ✅ **Clickable titles** that open Reddit posts in new tabs
- ✅ **Rich metadata**: subreddit, author, score, date, post type
- ✅ **Comment previews** for saved comments with special styling
- ✅ **Statistics** showing total count and generation timestamp
- ✅ **Self-contained** - works offline, no dependencies
- ✅ **Import-ready** for bookmark managers like Chrome, Firefox

**Perfect for:**
- Personal archives and offline viewing
- Importing into browser bookmarks
- Sharing your curated content with others
- Creating a searchable local database of saved posts

---

## Troubleshooting

### Authentication Issues

**Error: "No authentication tokens found"**
- **CLI**: Make sure `tokens.json` exists in project directory
- **Docker**: Ensure `tokens.json` is in the `data/` directory
- **Solution**: Regenerate tokens with `python generate_tokens.py`

**Error: "Failed to refresh access token"**
- Delete `tokens.json` and regenerate tokens
- Check that your Reddit app credentials are correct

### Docker Issues

**Error: "Cannot open web browser" in Docker**
- This is expected! Docker containers can't open browsers
- You must generate tokens on a computer with a browser first (Step 1)

**Error: "Permission denied" in Docker**
- Fix file permissions: `chmod 644 tokens.json .env`
- Fix directory permissions: `chmod 755 data/`

**Error: "File not found" in Docker**
- Verify file structure matches the example above
- Ensure `.env` and `tokens.json` are in correct locations

### General Issues

**"No new posts found"**
- Check if you have new saved posts on Reddit
- Try force fetch: Set `FORCE_FETCH=true`
- Verify `REDDIT_USERNAME` in `.env` is correct

**"Headless system detected" on desktop**
- Override detection: `REDDIT_FETCHER_HEADLESS=false reddit-fetcher`

---

## Method Comparison

| Feature | CLI Script | Build Docker | Pre-built Docker |
|---------|------------|--------------|------------------|
| **Setup Time** | Fast | Medium | Fast |
| **Customization** | Full | Full | Limited |
| **Dependencies** | Python required | Docker only | Docker only |
| **Auto-scheduling** | Manual/cron | Built-in | Built-in |
| **Updates** | Git pull | Rebuild image | Pull new image |
| **Best for** | Development | Custom needs | Production |

---

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details.
