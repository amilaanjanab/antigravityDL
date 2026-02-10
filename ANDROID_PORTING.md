# Android Porting Guide for GravityDownloader

## 1. The Challenge
Your current application uses **Eel**, which acts as a bridge between Python and a Desktop Browser. Android does not work this way. To run on Android, the application must be "compiled" using a framework that bundles Python inside an APK.

### Critical Limitations on Android
*   **No Auto-Login**: You cannot use `browser_cookie3` to "steal" cookies from Chrome/Brave on Android. The OS forbids this for security.
    *   *Workaround*: You would need to export a `cookies.txt` file on your PC and transfer it to your phone manually.
*   **No Eel**: You must replace the `eel` UI layer with something else.

## 2. Recommended Stack: Kivy + Buildozer
The standard way to turn a Python script into an APK is **Kivy**.

### Step 1: The UI Rewrite
You cannot use your `index.html` directly as a native app interface without a WebView wrapper.
*   **Approach A (Native)**: Rewrite the HTML/CSS UI into **Kivy Language (.kv)**. This gives the best performance.
*   **Approach B (WebView)**: Use Kivy to launch a simple window that displays your `index.html` (requires a local mini-server running on the phone).

### Step 2: The Dependencies
You need to tell the compiler to include:
*   `python3`
*   `yt-dlp`
*   `ffmpeg` (This is the hard part - bundling FFmpeg on Android is difficult but possible).

## 3. How to Build (Requires Linux or Mac)
You cannot easily build an APK on Windows. You need **WSL (Windows Subsystem for Linux)**.

1.  **Install WSL**: `wsl --install`
2.  **Install Buildozer**: `pip install buildozer`
3.  **Init Project**: `buildozer init`
4.  **Edit `buildozer.spec`**:
    *   Add permissions: `INTERNET`, `WRITE_EXTERNAL_STORAGE`
    *   Add requirements: `python3,kivy,yt-dlp,ffmpeg`
5.  **Compile**: `buildozer android debug`

## 4. Alternative: Termux (The Hacker Way)
If you just want to *use* the tool on your phone and don't care about it looking like a "real" app icon:

1.  Install **Termux** from F-Droid.
2.  Run: `pkg install python ffmpeg`
3.  Copy your `main.py` to the phone.
4.  Run: `python main.py`
    *   *Note*: You would need to remove the `eel` UI code and make a simple Command Line Interface (CLI) instead.

## Summary
To make this a real APK, we would effectively be starting a **new project** specifically for mobile, stripping out the Desktop-only features (Eel, Auto-Auth) and rebuilding the inputs for touch screens.
