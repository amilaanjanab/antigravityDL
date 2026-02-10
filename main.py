import eel
import yt_dlp
import threading
import sys
import os

# Try to import browser_cookie3, handle if missing
try:
    import browser_cookie3
    HAS_COOKIES = True
except ImportError:
    HAS_COOKIES = False

# Initialize Eel with the web folder
eel.init('web')

import re
import json
import time

# Global Cancellation Flag
CANCEL_FLAG = False
CONFIG_FILE = 'config.json'

# Load Config Defaults
TARGET_BROWSER = 'auto'
TARGET_PROFILE = ''
DOWNLOAD_PATH = 'downloads'

def load_config():
    global TARGET_BROWSER, TARGET_PROFILE, DOWNLOAD_PATH
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                TARGET_BROWSER = data.get('browser', 'auto')
                TARGET_PROFILE = data.get('profile', '')
                DOWNLOAD_PATH = data.get('download_path', 'downloads')
        except:
            pass # Use defaults
            
    # Ensure download directory exists
    if not os.path.exists(DOWNLOAD_PATH):
        try:
            os.makedirs(DOWNLOAD_PATH)
        except:
            pass

load_config() # Initial Load

def remove_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

# ... (progress_hook) ...
def progress_hook(d):
    """
    Callback for yt-dlp to monitor download progress.
    Sends percentage updates to the UI, including playlist info.
    CHECKS FOR CANCELLATION.
    """
    global CANCEL_FLAG
    if CANCEL_FLAG:
        raise Exception("ABORTED_BY_USER")

    if d['status'] == 'downloading':
        try:
            # Safe calculation of percentage
            raw_percent = d.get('_percent_str', '0%')
            clean_percent = remove_ansi(raw_percent).replace('%', '').strip()
            p = float(clean_percent)
            
            # Playlist Info
            index = d.get('playlist_index')
            count = d.get('playlist_count')
            
            # Speed Info
            raw_speed = d.get('_speed_str', 'CALC...')
            clean_speed = remove_ansi(raw_speed).strip()
            speed_display = f"SPD: {clean_speed}"
            
            # Construct status string
            status_msg = ""
            if index and count:
                status_msg = f"ABSORBING [{index}/{count}]"
            
            eel.update_progress(p, status_msg, speed_display)
        except Exception as e:
            if d.get('total_bytes') and d.get('downloaded_bytes'):
                p = (d['downloaded_bytes'] / d['total_bytes']) * 100
                eel.update_progress(p, None, None)
            else:
                # print(f"Progress Error: {e}")
                pass
    elif d['status'] == 'finished':
        eel.update_progress(100.0, "FINALIZING SHARD...", "COMPLETE")
        eel.log_message("Processing finished. Converting/Saving...")

@eel.expose
def save_config(browser, profile_path, download_path):
    global TARGET_BROWSER, TARGET_PROFILE, DOWNLOAD_PATH
    TARGET_BROWSER = browser
    TARGET_PROFILE = profile_path
    
    # Normalize path
    if not download_path or not download_path.strip():
        download_path = 'downloads'
    DOWNLOAD_PATH = download_path
    
    # Create if missing
    if not os.path.exists(DOWNLOAD_PATH):
        try:
            os.makedirs(DOWNLOAD_PATH)
        except Exception as e:
            eel.log_message(f"Error creating directory: {e}")
    
    # Save to disk
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            'browser': browser, 
            'profile': profile_path,
            'download_path': DOWNLOAD_PATH
        }, f)
    
    eel.log_message("Config Saved. Restarting System...")

@eel.expose
def get_config():
    """Returns current config to UI"""
    return {
        'browser': TARGET_BROWSER, 
        'profile': TARGET_PROFILE,
        'download_path': DOWNLOAD_PATH
    }

@eel.expose
def restart_app():
    """Restarts the current program."""
    print("RESTARTING APPLICATION...")
    time.sleep(1)
    python = sys.executable
    os.execl(python, python, *sys.argv)

@eel.expose
def cancel_process():
    global CANCEL_FLAG
    CANCEL_FLAG = True

def _download_worker(url, format_type, quality):
    """
    download worker.
    """
    global TARGET_BROWSER, TARGET_PROFILE, DOWNLOAD_PATH
    
    # Ensure download path exists
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    # Base Options
    ydl_opts = {
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
        'noplaylist': False,
        'writedescription': True, # Save description
        'writethumbnail': False,   # Disable to avoid video covers
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'ignoreerrors': True, # Skip failed items
    }

    # Format Logic
    if format_type == 'audio':
        # Audio Mode (MP3) - Stays same
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        # Video/Media Mode
        if quality == 'best':
            # HYBRID MODE: We do NOT specify 'format' or 'merge_output_format'.
            # This lets yt-dlp download images (jpg) OR videos (mp4) naturally.
            pass
        else:
            # Specific Resolution (still mostly video focused)
            ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
            ydl_opts['merge_output_format'] = 'mp4'

    # --- AUTHENTICATION LOGIC ---
    # Smart Switch: browser_cookie3 is often better at handling locked files than yt-dlp native
    cookies = None
    if HAS_COOKIES:
        eel.log_message(f"AUTH TARGET: {TARGET_BROWSER.upper()} (Python Bridge)")
        try:
            c = None
            if TARGET_BROWSER == 'brave':
                c = browser_cookie3.brave(cookie_file=TARGET_PROFILE if TARGET_PROFILE else None)
            elif TARGET_BROWSER == 'chrome':
                c = browser_cookie3.chrome(cookie_file=TARGET_PROFILE if TARGET_PROFILE else None)
            elif TARGET_BROWSER == 'edge':
                c = browser_cookie3.edge(cookie_file=TARGET_PROFILE if TARGET_PROFILE else None)
            elif TARGET_BROWSER == 'firefox':
                c = browser_cookie3.firefox(cookie_file=TARGET_PROFILE if TARGET_PROFILE else None)
            elif TARGET_BROWSER == 'opera':
                c = browser_cookie3.opera(cookie_file=TARGET_PROFILE if TARGET_PROFILE else None)
            elif TARGET_BROWSER == 'auto':
                 # Try Brave first as it's the user's preference, then Chrome
                try: c = browser_cookie3.brave()
                except: 
                    try: c = browser_cookie3.chrome()
                    except: c = browser_cookie3.load() # Generic
            
            if c:
                cookies = c
                eel.log_message("Secure Session Extracted Successfully.")
            else:
                eel.log_message("Warning: Cookie Jar was empty or None.")
                
        except Exception as e:
            eel.log_message(f"Auth Extraction Failed: {e}")
            # print(f"Auth Error: {e}")
    
    if cookies:
        ydl_opts['cookiejar'] = cookies
    else:
        # Fallback to anonymous if auth failed
        eel.log_message("Proceeding with ANONYMOUS connection.")
        if 'cookiesfrombrowser' in ydl_opts:
            del ydl_opts['cookiesfrombrowser']

    # ... (rest of function) ...
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            eel.log_message("Analyzing Metadata...")
            ydl.download([url])
            
        # POST-PROCESSING: Convert .description to .txt
        try:
            for file in os.listdir(DOWNLOAD_PATH):
                if file.endswith(".description"):
                    base = os.path.splitext(file)[0]
                    src = os.path.join(DOWNLOAD_PATH, file)
                    dst = os.path.join(DOWNLOAD_PATH, base + ".txt")
                    if not os.path.exists(dst):
                         import shutil
                         shutil.copy2(src, dst)
        except Exception as e:
            print(f"Text Conversion Error: {e}")

        eel.download_complete()
    # ... (error handling) ...
    except Exception as e:
        # Check for our custom abort message
        if "ABORTED_BY_USER" in str(e):
            eel.log_error("PROTOCOL ABORTED BY USER.")
        elif isinstance(e, yt_dlp.utils.DownloadError):
            error_msg = str(e)
            if "403" in error_msg:
                 eel.log_error("Error 403: Forbidden. Server rejected request.")
            else:
                 eel.log_error(f"Download Error: {error_msg}")
        else:
            eel.log_error(f"System Error: {str(e)}")

@eel.expose
def fetch_metadata(url):
    """
    Fetches video metadata without downloading.
    Returns JSON object to JS.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist', # Just extract info
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Handle Playlists vs Single Video
            if 'entries' in info:
                # It's a playlist or channel
                title = info.get('title', 'Unknown Playlist')
                
                # Safe entry handling
                entries = list(info.get('entries', []))
                count = len(entries)
                
                # Thumbnail Strategy: Playlist -> First Entry Simple -> First Entry List
                thumbnail = info.get('thumbnail')
                
                if not thumbnail and entries:
                    first_entry = entries[0]
                    thumbnail = first_entry.get('thumbnail')
                    
                    # If still empty, check deeply into 'thumbnails' list
                    if not thumbnail:
                        thumbs = first_entry.get('thumbnails', [])
                        if thumbs and isinstance(thumbs, list):
                            # Try to get the last one (usually highest quality)
                            thumbnail = thumbs[-1].get('url')

                duration = f"{count} Videos"
                uploader = info.get('uploader', 'Playlist')
            else:
                # Single Video
                title = info.get('title', 'Unknown Title')
                thumbnail = info.get('thumbnail', '')
                duration = info.get('duration_string', 'N/A')
                uploader = info.get('uploader', 'Unknown Source')
            
            # Final Fallback
            if not thumbnail:
                thumbnail = "" # Ensure it's not None at least
            
            return {
                'success': True,
                'title': title,
                'thumbnail': thumbnail,
                'duration': duration,
                'uploader': uploader
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@eel.expose
def start_download(url, format_type='video', quality='best'):
    """
    Entry point from UI. Spawns a thread to prevent blocking.
    """
    # Validation Protocol
    if not url or not isinstance(url, str):
        eel.log_error("Invalid URL provided.")
        return

    # Threading: ESSENTIAL for non-blocking UI
    t = threading.Thread(target=_download_worker, args=(url, format_type, quality))
    t.daemon = True
    t.start()

def get_browser_binary(browser_name):
    """
    Attempts to find the executable path for specific browsers on Windows.
    """
    browser_name = browser_name.lower()
    paths = []
    
    if 'brave' in browser_name:
        paths = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
        ]
    elif 'opera' in browser_name:
        paths = [
            os.path.expanduser(r"~\AppData\Local\Programs\Opera\launcher.exe"),
            os.path.expanduser(r"~\AppData\Local\Programs\Opera GX\launcher.exe")
        ]
        
    for path in paths:
        if os.path.exists(path):
            return path
    return None

if __name__ == '__main__':
    # GUI LAUNCH PROTOCOL
    # Restoring User Control over the Interface
    
    gui_mode = 'chrome' # Default fallback
    
    # 1. Edge
    if TARGET_BROWSER in ['edge', 'microsoft-edge']:
        gui_mode = 'edge'
        
    # 2. Firefox (Limited App Mode Support)
    elif TARGET_BROWSER in ['firefox', 'mozilla']:
        gui_mode = 'default' 
        
    # 3. Brave / Opera (Chromium variants)
    elif TARGET_BROWSER in ['brave', 'opera']:
        # Try to find the specific binary to force Eel to use it
        bin_path = get_browser_binary(TARGET_BROWSER)
        if bin_path:
            # Force Eel to use this binary
            eel.browsers.set_path('chrome', bin_path)
            gui_mode = 'chrome'
            print(f"GUI OVERRIDE: Using {TARGET_BROWSER} at {bin_path}")
        else:
            print(f"GUI WARNING: Could not find {TARGET_BROWSER} binary. Launching with default Chrome engine.")
            gui_mode = 'chrome'

    # 4. Standard Chrome
    elif TARGET_BROWSER in ['chrome', 'google-chrome', 'chromium']:
        gui_mode = 'chrome'
    
    print(f"LAUNCHING GUI IN MODE: {gui_mode.upper()}")
    print(f"AUTH TARGET FOR DOWNLOADS: {TARGET_BROWSER.upper()}")
    
    try:
        eel.start('index.html', size=(900, 700), mode=gui_mode)
    except Exception as e:
        print(f"Primary Launch Failed ({gui_mode}): {e}")
        # Fallback to system default
        eel.start('index.html', size=(900, 700), mode='default')
