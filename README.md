
# Reddit Saved Posts Fetcher

## 📌 Overview

This script allows users to **fetch their saved Reddit posts and comments** using the Reddit API with OAuth authentication. It automatically retrieves new saved posts and stores them in a local text file, maintaining a **delta-fetching mechanism** to avoid duplicate retrieval.

### **💡 Use Cases**

* **Backup your saved Reddit posts** locally for reference.
* **Organize and analyze saved posts** without relying on Reddit.
* **Automate Reddit data extraction** for research purposes.

---

## 🔧 Setup & Installation

### **1️⃣ Clone the Repository**

First, clone this repository to your local or headless server environment:

```bash
git clone https://github.com/jayjay3108/Reddit-Fetch.git
cd Reddit-Fetcher
```

### **2️⃣ Prerequisites**

* **Python 3.x** installed on your system.
* Install required dependencies:
  ```bash
  pip install -r requirements.txt
  ```

#### **Contents of `requirements.txt`**

* `requests` - For making API calls to Reddit.
* `python-dotenv` - For managing environment variables securely.

### **3️⃣ Setting Up Reddit API Credentials**

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps) and click  **Create App** .
2. Choose **Web App** as the application type.
3. Enter an **App Name** (e.g., `Reddit Saved Posts Fetcher`).
4. Set the **Redirect URI** to: `http://localhost:8080`
5. Click  **Create App** .
6. Copy the **Client ID** (found under the app name) and  **Client Secret** .

### **4️⃣ Configure `.env` File**

Create a `.env` file in the project directory and add the following:

```ini
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://localhost:8080
USER_AGENT=YourRedditApp/1.0 (by /u/your_username)
REDDIT_USERNAME=your_reddit_username
```

---

## 🔑 Authentication & Token Handling

### **1️⃣ First-time Authentication (Desktop Mode)**

1. Run `generate_tokens.py` to  **generate `tokens.json`** :

```bash
python generate_tokens.py
```

2. This will **open a browser window** for authorization.
3. After authentication, a `tokens.json` file will be generated containing the  **refresh token** .
4. Run `main.py` to fetch your saved posts:

```bash
python main.py
```

### **2️⃣ Running on a Headless Server**

1. **Run `generate_tokens.py` on a Windows or Desktop machine** to generate `tokens.json`.
2. **Copy `tokens.json`** to your headless server:
   ```bash
   scp tokens.json user@your-server:/path/to/reddit-fetcher/
   ```
3. **On the headless server, navigate to the script directory and run:**
   ```bash
   cd /path/to/reddit-fetcher
   python main.py
   ```

* The script will use the copied `tokens.json` to fetch new access tokens automatically.

### **3️⃣ Handling Token Expiration**

* Access tokens expire **every 1 hour** but are  **automatically refreshed** .
* If the refresh token becomes invalid,  **re-run `generate_tokens.py`** .

---

## 🚀 Running the Script

To fetch  **new saved posts** , run:

```bash
python main.py
```

### **What Happens?**

✅ **Checks for existing tokens** and refreshes if needed.

✅ **Fetches only new saved posts** since the last run.

✅ **Appends posts and comments** to `saved_posts.txt`.

---

## 📂 Data Storage

| File                | Purpose                                 |
| ------------------- | --------------------------------------- |
| `tokens.json`     | Stores refresh token for authentication |
| `saved_posts.txt` | Contains retrieved posts and comments   |
| `last_fetch.json` | Tracks last fetch timestamp             |

---

## 🛠️ Advanced Features

* **Delta Fetching** : Avoids duplicate retrieval by checking timestamps.
* **Automated Execution** : Can be scheduled via **cron jobs** or  **Windows Task Scheduler** .
* **Headless Server Support** : Easily run on cloud servers or Raspberry Pi.

---

## 🔍 Troubleshooting

### **1️⃣ Token Errors**

* If `tokens.json` is empty or corrupted, **delete it** and re-run `generate_tokens.py`.
* Ensure the **correct Reddit API credentials** are set in `.env`.

### **2️⃣ Fetching Issues**

* Ensure the **correct username** is set in `config.py`.
* Check if Reddit API rate limits have been hit.

---

## 📌 Future Enhancements

* **Web UI for browsing saved posts** .
* **Content summarization using AI** .
* **Better retry mechanisms for API errors** .

---

💡 **Contributions and feedback are welcome!** 🚀
