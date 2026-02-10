# Project Specification: GravityDownloader (Eel Edition)

## 1. Project Overview
A high-performance, minimalist desktop video downloader using Python (Backend) and HTML/CSS/JS (Frontend). The interface features "Antigravity" physics-inspired aesthetics (floating elements, glassmorphism) and leverages `yt-dlp` for downloading and `browser_cookie3` for authentication bypass.

## 2. Technical Stack
* **Backend:** Python 3.10+
* **Bridge:** `Eel` (Python-to-JS communication)
* **Core Engine:** `yt-dlp` (Video extraction)
* **Authentication:** `browser_cookie3` (Auto-extract cookies from Chrome/Firefox/Edge)
* **Frontend:** HTML5, CSS3 (Flexbox/Grid, Keyframe Animations), Vanilla JavaScript (ES6+)

## 3. UI/UX Design System
* **Theme:** "Dark Glass." Deep grey/black backgrounds with high transparency and blur (`backdrop-filter: blur(10px)`).
* **Typography:** Monospace (e.g., 'Courier New', 'Fira Code') for a "Hacker/Terminal" feel, mixed with Sans-Serif for readability.
* **Antigravity Effect:** The search bar and status cards must "float" using CSS animations (slow vertical bobbing).
* **Interactivity:**
    1.  **Input:** User pastes URL.
    2.  **Preview Phase:** App fetches metadata (Thumbnail, Title, Duration) and displays a "Floating Card."
    3.  **Action:** User clicks "Absorb" (Download).
    4.  **Process:** Progress bar fills; particles emit on completion.

## 4. Functional Requirements

### A. Python Backend (`main.py`)
1.  **`fetch_metadata(url)`**:
    * Runs `yt-dlp --dump-json` (fast, no download).
    * Returns JSON: `{title, thumbnail, duration, site}`.
    * *Error Handling:* If URL is invalid, return generic error structure.
2.  **`download_video(url)`**:
    * **Threading:** MUST run in a separate thread to prevent UI freezing.
    * **Cookies:** Attempt `browser_cookie3.load()` to bypass age/login restrictions.
    * **Progress Hook:** A custom callback function in `yt-dlp` that calculates percentage and calls `eel.update_progress(percent)`.
    * **FFmpeg Check:** Verify FFmpeg is installed/detected before starting.

### B. JavaScript Frontend (`script.js`)
1.  **State Management:** Handle `Idle`, `Fetching`, `Downloading`, `Error`, `Success` states.
2.  **Eel Exposure:** Expose functions `update_progress(n)` and `log_error(msg)` to Python.
3.  **Bug Detection:** If progress hangs at 0% for >10s, display a "Timeout/Network" warning.

## 5. Error Handling Protocols
* **Protocol 403 (Forbidden):** If `yt-dlp` returns 403, retry with a generic User-Agent string.
* **Protocol No-Cookies:** If `browser_cookie3` fails, fallback to anonymous download and warn user "Restricted Content May Fail."
* **Protocol Invalid URL:** Regex check URL before sending to Python.

## 6. Directory Structure
```text
/GravityDownloader
│
├── main.py                # Entry point, Eel setup, yt-dlp wrapper
├── requirements.txt       # eel, yt-dlp, browser-cookie3
│
└── /web
    ├── index.html         # Semantic HTML structure
    ├── style.css          # CSS Variables, Animations, Glassmorphism
    ├── script.js          # Eel bindings, UI logic
    └── /assets            # Icons (SVG)