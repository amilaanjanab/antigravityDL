# How to Add Screenshots to Your GitHub Repository

## Method 1: Add Screenshots Manually (Recommended)

### Step 1: Take Screenshots
1. Run your application
2. Use **Windows + Shift + S** to take screenshots
3. Save them to `d:/VS_Code/AnyVideoDownloader/screenshots/` folder
4. Name them descriptively:
   - `main-interface.png`
   - `download-progress.png`
   - `settings.png`
   - etc.

### Step 2: Add Screenshots to Git
```bash
cd d:/VS_Code/AnyVideoDownloader
git add screenshots/
git commit -m "Add application screenshots"
git push
```

### Step 3: Reference Screenshots in README
In your `README.md`, add:

```markdown
## Screenshots

### Main Interface
![Main Interface](screenshots/main-interface.png)

### Download in Progress
![Download Progress](screenshots/download-progress.png)

### Settings
![Settings](screenshots/settings.png)
```

## Method 2: Using GitHub's Web Interface

1. Go to your repository on GitHub
2. Navigate to the `screenshots` folder
3. Click **Add file** → **Upload files**
4. Drag and drop your screenshots
5. Commit the changes

## Method 3: Using Markdown with Direct Image Upload

When editing `README.md` on GitHub:
1. Click the **Edit** button (pencil icon)
2. Drag and drop images directly into the editor
3. GitHub will automatically upload and create markdown links
4. Commit the changes

## Tips for Good Screenshots

✅ **Use high resolution** (but not too large, keep under 1MB each)  
✅ **Show key features** of your application  
✅ **Use descriptive filenames** (no spaces, use hyphens)  
✅ **Crop unnecessary parts** (focus on the app)  
✅ **Consider using a GIF** for showing download progress  

## Recommended Screenshot Tools

- **Windows Snipping Tool** (Built-in)
- **ShareX** (Free, powerful)
- **Greenshot** (Free, open-source)
- **ScreenToGif** (For animated GIFs)
