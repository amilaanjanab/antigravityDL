let currentUrl = "";
let currentMeta = {}; // Store title/thumb for transfer

// Load initial settings (Optional: Implement get_settings logic if needed, 
// for now standard modal shows defaults)


// --- Eel Exposed Functions (Python to JS) ---

eel.expose(update_progress);
function update_progress(percent, status_msg, speed) {
    const bar = document.getElementById('progress-fill');
    const text = document.getElementById('percent-text');

    // Prevent backsliding but allow resets
    if (percent === 0) {
        bar.style.width = '0%';
        text.innerText = '0%';
    } else {
        bar.style.width = percent + '%';
        text.innerText = Math.round(percent) + '%';
    }

    // Update status text
    if (status_msg) {
        document.getElementById('status-text').innerText = status_msg;
    }

    // Update Speed if provided
    if (speed) {
        document.getElementById('speed-text').innerText = speed;
    }

    if (percent >= 100 && !status_msg) {
        document.getElementById('status-text').innerText = "ABSORBED";
        document.getElementById('speed-text').innerText = "DATA SECURED";
        document.getElementById('absorb-btn').innerText = "DONE";
    }
}

eel.expose(log_message);
function log_message(msg) {
    document.getElementById('status-text').innerText = msg;
}

eel.expose(log_error);
function log_error(msg) {
    const logDiv = document.getElementById('log-display');
    logDiv.innerText = msg;
    logDiv.classList.remove('hidden');

    // Revert UI from "Downloading" to "Preview" if fails
    document.getElementById('progress-section').classList.add('hidden');
    document.getElementById('preview-section').classList.remove('hidden');
}

eel.expose(download_complete);
function download_complete() {
    document.getElementById('status-text').innerText = "COMPLETE";
    // Using Custom Modal instead of Alert
    showCustomAlert("Download Successful! Data Secured.");
    resetView();
}

// --- UI Logic (JS to Python) ---

async function scanUrl() {
    const input = document.getElementById('url-input');
    const url = input.value.trim();

    if (!url) {
        log_error("Protocol Error: Input Empty");
        return;
    }

    // UI Transition: Input -> Loading
    const btn = document.getElementById('scan-btn');
    const originalText = btn.innerText;
    btn.innerText = "...";
    btn.disabled = true;

    // Clear previous errors
    document.getElementById('log-display').classList.add('hidden');

    // Call Python
    let data = await eel.fetch_metadata(url)();

    if (data.success) {
        currentUrl = url;
        currentMeta = data; // Save for later
        showPreview(data);
    } else {
        log_error("Scan Failed: " + data.error);
    }

    // Reset Button
    btn.innerText = originalText;
    btn.disabled = false;
}

function showPreview(data) {
    // Hide Input, Show Preview
    document.getElementById('input-section').classList.add('hidden');
    document.getElementById('preview-section').classList.remove('hidden');

    // Populate Data
    document.getElementById('video-title').innerText = data.title;
    document.getElementById('thumb-img').src = data.thumbnail;
    document.getElementById('video-meta').innerText = `Duration: ${data.duration} | Uploader: ${data.uploader}`;
}

function initiateDownload() {
    if (!currentUrl) return;

    // Get User Selection
    const format = document.getElementById('format-select').value;
    const quality = document.getElementById('quality-select').value;

    // UI Transition: Preview -> Progress
    document.getElementById('preview-section').classList.add('hidden');
    document.getElementById('progress-section').classList.remove('hidden');

    // Reset bar
    update_progress(0);
    document.getElementById('status-text').innerText = "INITIATING PARADIGM SHIFT...";
    document.getElementById('speed-text').innerText = "CONN: ESTABLISHING...";

    // Populate Active View
    document.getElementById('active-title').innerText = currentMeta.title || "Target Locked";
    document.getElementById('active-thumb').src = currentMeta.thumbnail || "";

    // Call Python (Non-blocking)
    eel.start_download(currentUrl, format, quality);
}

function resetView() {
    currentUrl = "";
    document.getElementById('url-input').value = "";
    document.getElementById('progress-section').classList.add('hidden');
    document.getElementById('preview-section').classList.add('hidden');
    document.getElementById('log-display').classList.add('hidden');
    document.getElementById('input-section').classList.remove('hidden');
    document.getElementById('absorb-btn').innerText = "ABSORB";
}

function requestAbort() {
    // Notify Python
    eel.cancel_process();
    // Immediate UI feedback
    document.getElementById('status-text').innerText = "ABORTING...";
}

// --- Settings Logic ---

// --- Settings Logic ---

async function toggleSettings() {
    const modal = document.getElementById('settings-modal');
    modal.classList.toggle('hidden');

    if (!modal.classList.contains('hidden')) {
        // Load current config
        let config = await eel.get_config()();
        if (config) {
            document.getElementById('browser-select').value = config.browser;
            document.getElementById('profile-path').value = config.profile;
            // Check if element exists before setting (robustness)
            const dlInput = document.getElementById('download-path');
            if (dlInput && config.download_path) dlInput.value = config.download_path;
        }
    }
}

async function saveSettings() {
    const browser = document.getElementById('browser-select').value;
    const profile_path = document.getElementById('profile-path').value.trim();
    const download_path = document.getElementById('download-path').value.trim();

    document.getElementById('status-text').innerText = "WRITING CONFIG...";

    // Save Config
    await eel.save_config(browser, profile_path, download_path)();

    // Trigger Restart
    showCustomAlert("Config Saved. System Restarting in 2s...");
    setTimeout(() => {
        eel.restart_app();
    }, 2000);
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    // Enable Enter Key for URL Input
    const urlInput = document.getElementById('url-input');
    if (urlInput) {
        urlInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent default form submission if any
                document.getElementById('scan-btn').click(); // Simulate click
            }
        });
    }
});

// --- Custom Alert Logic ---
function showCustomAlert(msg) {
    const modal = document.getElementById('custom-alert');
    const msgElement = document.getElementById('alert-msg');

    if (modal && msgElement) {
        msgElement.innerText = msg;
        modal.classList.remove('hidden');
    } else {
        // Fallback if HTML missing
        alert(msg);
    }
}

function closeCustomAlert() {
    document.getElementById('custom-alert').classList.add('hidden');
}
