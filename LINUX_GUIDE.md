# Linux Installation & Usage Guide

## 🐧 Step-by-Step Setup

1. **Update Packages**  
   ```bash
   sudo apt update && sudo apt upgrade -y  # Debian/Ubuntu
   # OR
   sudo dnf update -y  # Fedora
   ```

2. **Install Python**  
   ```bash
   sudo apt install python3.12 python3-pip -y  # Debian/Ubuntu
   # OR
   sudo dnf install python3.12 python3-pip -y  # Fedora
   ```

3. **Install Required Package**  
   ```bash
   python3 -m pip install requests
   ```

4. **Create Configuration File**  
   ```bash
   nano config.json
   ```
   Paste:
   ```json
   {
     "radarr_ip": "localhost",
     "radarr_port": "7878",
     "radarr_api_key": "YOUR_KEY_HERE"
   }
   ```
   ^O to save, ^X to exit

5. **Download Script**  
   ```bash
   wget https://raw.githubusercontent.com/bizzkoot/radarr_cleanup/main/radarr_cleanup.py
   ```

## 🏃 Running the Script
```bash
# Normal mode
python3 radarr_cleanup.py

# Dry-run mode (safe test)
python3 radarr_cleanup.py --dry-run
```

## 🛠️ Troubleshooting
| Issue | Fix |
|-------|-----|
| "Permission denied" | `chmod +x radarr_cleanup.py` |
| Python version mismatch | Use `python3.12` explicitly |
| Missing dependencies | `sudo apt install python3.12-venv` |

[Back to Main README](../README.md)
