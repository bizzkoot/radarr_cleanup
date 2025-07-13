# Windows Installation & Usage Guide

## 🔧 Step-by-Step Setup

1. **Install Python**  
   Choose one method:
   - **Microsoft Store** (Recommended):  
     Search for "Python 3.12" in Start Menu → Click Install
   - **Manual Install**:  
     [Download Python](https://www.python.org/downloads/windows/) →  
     ✅ Check "Add Python to PATH" during installation

2. **Open PowerShell**  
   Right-click Start → Windows PowerShell (Admin)

3. **Install Required Package**  
   ```powershell
   python -m pip install requests
   ```

4. **Create Configuration File**  
   ```powershell
   New-Item config.json -Value @'
   {
     "radarr_ip": "localhost",
     "radarr_port": "7878",
     "radarr_api_key": "YOUR_KEY_HERE",
     "max_runtime_minutes": 120
   }
   '@
   ```
   🔑 Replace YOUR_KEY_HERE with [your Radarr API key](http://localhost:7878/settings/general)

5. **Download Script**  
   Right-click → Save As:  
   [radarr_cleanup.py](https://raw.githubusercontent.com/bizzkoot/radarr_cleanup/main/radarr_cleanup.py)

## 🏃 Running the Script
```powershell
# Normal mode
python radarr_cleanup.py

# Dry-run mode (safe test)
python radarr_cleanup.py --dry-run
```

## 🛠️ Troubleshooting
| Issue | Fix |
|-------|-----|
| "Python not found" | Reinstall with "Add to PATH" checked |
| Permission denied | Right-click PowerShell → Run as Administrator |
| Connection errors | Check Windows Firewall allows Python |

[Back to Main README](../README.md)