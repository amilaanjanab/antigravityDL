# How to Publish AntigravityDL to PyPI

## 📦 Package Files Ready!

Your Python package has been built successfully:
- `dist/antigravitydl-1.0.0.tar.gz` - Source distribution
- `dist/antigravitydl-1.0.0-py3-none-any.whl` - Wheel distribution

## 🚀 Publishing to PyPI

### Option 1: Test PyPI First (Recommended)

1. **Install twine** (if not already installed):
```bash
pip install twine
```

2. **Create TestPyPI account**:
   - Go to: https://test.pypi.org/account/register/
   - Verify your email

3. **Upload to TestPyPI**:
```bash
python -m twine upload --repository testpypi dist/*
```

4. **Test installation**:
```bash
pip install --index-url https://test.pypi.org/simple/ antigravitydl
```

5. **Test the command**:
```bash
antigravitydl
```

### Option 2: Publish to Real PyPI

1. **Create PyPI account**:
   - Go to: https://pypi.org/account/register/
   - Verify your email

2. **Upload to PyPI**:
```bash
python -m twine upload dist/*
```

3. **Users can now install with**:
```bash
pip install antigravitydl
```

## 🎯 After Publishing

Users can install and run your app with:

```bash
# Install
pip install antigravitydl

# Run
antigravitydl
```

That's it! No need to clone the repo or manually install dependencies!

## 📝 Package Information

- **Package Name**: `antigravitydl`
- **Version**: 1.0.0
- **Command**: `antigravitydl`
- **PyPI URL** (after publishing): https://pypi.org/project/antigravitydl/

## 🔄 Updating the Package

When you make changes:

1. Update version in `pyproject.toml`
2. Rebuild:
   ```bash
   python -m build
   ```
3. Upload new version:
   ```bash
   python -m twine upload dist/*
   ```

## ⚠️ Important Notes

- **Package name must be unique** on PyPI
- If `antigravitydl` is taken, you might need to use a different name
- You can check availability at: https://pypi.org/project/antigravitydl/
- Consider using `antigravity-dl` or `antigravity-downloader` if needed

## 🎁 What Users Get

After `pip install antigravitydl`, users get:
- ✅ All dependencies auto-installed (eel, yt-dlp, browser-cookie3)
- ✅ Command-line tool: `antigravitydl`
- ✅ Python module: `import antigravitydl`
- ✅ Web interface files included
- ✅ Works on Windows, Mac, and Linux!
