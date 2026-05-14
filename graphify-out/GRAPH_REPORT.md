# Graph Report - Reddit-Fetch  (2026-05-14)

## Corpus Check
- 6 files · ~6,169 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 47 nodes · 71 edges · 10 communities detected
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]

## God Nodes (most connected - your core abstractions)
1. `refresh_access_token_safe()` - 9 edges
2. `cli_entry()` - 8 edges
3. `show_headless_instructions()` - 7 edges
4. `get_new_tokens()` - 7 edges
5. `check_authentication()` - 7 edges
6. `is_headless()` - 6 edges
7. `make_request()` - 6 edges
8. `fetch_saved_posts()` - 6 edges
9. `is_docker()` - 5 edges
10. `load_tokens_safe()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `check_authentication()` --calls--> `is_headless()`  [INFERRED]
  reddit_fetch/main.py → reddit_fetch/auth.py
- `cli_entry()` --calls--> `is_headless()`  [INFERRED]
  reddit_fetch/main.py → reddit_fetch/auth.py
- `cli_entry()` --calls--> `is_docker()`  [INFERRED]
  reddit_fetch/main.py → reddit_fetch/auth.py
- `cli_entry()` --calls--> `show_headless_instructions()`  [INFERRED]
  reddit_fetch/main.py → reddit_fetch/auth.py
- `check_authentication()` --calls--> `load_tokens_safe()`  [INFERRED]
  reddit_fetch/main.py → reddit_fetch/auth.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.25
Nodes (10): fetch_saved_posts(), fetch_saved_posts_legacy(), generate_html_output(), get_valid_access_token(), make_request(), Fetch saved Reddit posts, using `after` for full fetch and `before` for incremen, Gets a valid access token, refreshing if necessary., Generate HTML output from posts list. (+2 more)

### Community 1 - "Community 1"
Cohesion: 0.38
Nodes (5): cli_entry(), is_interactive(), main(), Returns True if the script is running in an interactive terminal (TTY), Main entry point for the CLI.

### Community 2 - "Community 2"
Cohesion: 0.4
Nodes (6): is_docker(), Detects if running inside Docker container., Shows instructions for headless authentication., show_headless_instructions(), check_authentication(), Check if authentication is available and show appropriate messages.

### Community 3 - "Community 3"
Cohesion: 0.5
Nodes (4): get_new_tokens(), Validates Reddit API credentials format., Requests new authentication tokens via OAuth., validate_credentials()

### Community 4 - "Community 4"
Cohesion: 0.5
Nodes (4): load_tokens_safe(), Handles token loading safely, ensuring better error handling in headless mode., Refreshes the access token and handles headless system failures., refresh_access_token_safe()

### Community 5 - "Community 5"
Cohesion: 0.5
Nodes (2): AuthHandler, BaseHTTPRequestHandler

### Community 6 - "Community 6"
Cohesion: 0.67
Nodes (2): Start a temporary local web server to receive the OAuth callback., start_auth_server()

### Community 7 - "Community 7"
Cohesion: 0.67
Nodes (2): exponential_backoff(), Implements exponential backoff to avoid rate limiting.

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (2): is_headless(), Detects if the system is running in headless mode.

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (2): Safely saves tokens to `tokens.json`., save_tokens()

## Knowledge Gaps
- **18 isolated node(s):** `Detects if the system is running in headless mode.`, `Detects if running inside Docker container.`, `Shows instructions for headless authentication.`, `Handles token loading safely, ensuring better error handling in headless mode.`, `Safely saves tokens to `tokens.json`.` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 5`** (4 nodes): `AuthHandler`, `.do_GET()`, `.log_message()`, `BaseHTTPRequestHandler`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 6`** (3 nodes): `Start a temporary local web server to receive the OAuth callback.`, `start_auth_server()`, `auth.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 7`** (3 nodes): `exponential_backoff()`, `Implements exponential backoff to avoid rate limiting.`, `config.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (2 nodes): `is_headless()`, `Detects if the system is running in headless mode.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (2 nodes): `Safely saves tokens to `tokens.json`.`, `save_tokens()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cli_entry()` connect `Community 1` to `Community 8`, `Community 0`, `Community 2`?**
  _High betweenness centrality (0.277) - this node is a cross-community bridge._
- **Why does `refresh_access_token_safe()` connect `Community 4` to `Community 0`, `Community 2`, `Community 3`, `Community 6`, `Community 8`, `Community 9`?**
  _High betweenness centrality (0.238) - this node is a cross-community bridge._
- **Why does `make_request()` connect `Community 0` to `Community 4`, `Community 7`?**
  _High betweenness centrality (0.211) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `refresh_access_token_safe()` (e.g. with `get_valid_access_token()` and `make_request()`) actually correct?**
  _`refresh_access_token_safe()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `cli_entry()` (e.g. with `is_docker()` and `is_headless()`) actually correct?**
  _`cli_entry()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `show_headless_instructions()` (e.g. with `check_authentication()` and `cli_entry()`) actually correct?**
  _`show_headless_instructions()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `check_authentication()` (e.g. with `load_tokens_safe()` and `is_headless()`) actually correct?**
  _`check_authentication()` has 4 INFERRED edges - model-reasoned connections that need verification._