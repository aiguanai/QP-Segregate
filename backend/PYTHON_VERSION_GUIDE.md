# Python Version Guide for QPaper AI

## Recommended Python Version

**Python 3.11.x** (specifically 3.11.9 or latest 3.11.x)

### Why Python 3.11?
- ✅ Used in Dockerfile (`python:3.11-slim`)
- ✅ Well-supported by all dependencies
- ✅ Stable and widely tested
- ✅ All packages have pre-built wheels

## Installing Python 3.11 on Windows

### Option 1: Direct Download (Easiest)
1. Go to: https://www.python.org/downloads/release/python-3119/
2. Download "Windows installer (64-bit)"
3. Run installer
4. ✅ Check "Add Python to PATH"
5. Install

### Option 2: Using pyenv-win (For Multiple Versions)
```powershell
# Install pyenv-win
git clone https://github.com/pyenv-win/pyenv-win.git $HOME\.pyenv

# Add to PATH (PowerShell)
[System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
[System.Environment]::SetEnvironmentVariable('PYENV_ROOT',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
[System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
[System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims;" + [System.Environment]::GetEnvironmentVariable('path', "User"),"User")

# Install Python 3.11
pyenv install 3.11.9
pyenv local 3.11.9
```

## Setting Up Virtual Environment with Python 3.11

### If Python 3.11 is installed separately:
```powershell
# Find Python 3.11 path (usually in AppData or Program Files)
# Then create venv with specific Python
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

### If Python 3.11 is your default:
```powershell
# Remove old venv
Remove-Item -Recurse -Force venv

# Create new venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Verify version
python --version  # Should show Python 3.11.x
```

## Reinstalling Dependencies

After creating new venv with Python 3.11:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Download spaCy model
python -c "import spacy; spacy.cli.download('en_core_web_sm')"
```

## Verifying Installation

```powershell
python --version  # Should be 3.11.x
pip list  # Check packages installed
python -c "import fastapi, sqlalchemy, psycopg2; print('All imports OK')"
```

## Alternative: Python 3.12

If you can't get Python 3.11, Python 3.12 should also work:
- Download: https://www.python.org/downloads/release/python-3127/
- Follow same steps as above

## Troubleshooting

### "Python 3.11 not found"
- Make sure Python 3.11 is installed
- Check PATH environment variable
- Use full path: `C:\Python311\python.exe -m venv venv`

### "Still getting build errors"
- Make sure you're using Python 3.11 (not 3.14)
- Delete old `venv` folder completely
- Create fresh venv with Python 3.11
- Upgrade pip: `python -m pip install --upgrade pip setuptools wheel`

### "Multiple Python versions"
- Use `py -3.11` to specifically call Python 3.11
- Or use `pyenv-win` to manage versions

