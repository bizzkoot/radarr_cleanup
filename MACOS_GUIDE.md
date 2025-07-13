# macOS Installation & Usage Guide

## 🍎 Step-by-Step Setup

1. **Install Homebrew**  
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**  
   ```bash
   brew install python@3.12
   echo 'export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Install Required Package**  
   ```bash
   python3 -m pip install requests
   ```

4. **Create Project Folder**
   ```bash
   mkdir -p ~/radarr_cleanup
   cd ~/radarr_cleanup

5. **Create Configuration File**
   ```bash
   nano config.json
   ```
   Paste:
   ```json
   {
     "radarr_ip": "localhost",
     "radarr_port": "7878",
     "radarr_api_key": "YOUR_KEY_HERE",
     "max_runtime_minutes": 120
   }
   ```
   ^O to save, ^X to exit

6. **Download Script**
   ```bash
   curl -O https://raw.githubusercontent.com/bizzkoot/radarr_cleanup/main/radarr_cleanup.py
   ```

## 🏃 Running the Script
```bash
# Navigate to project folder
cd ~/radarr_cleanup

# Normal mode
python3 radarr_cleanup.py

# Dry-run mode (safe test)
python3 radarr_cleanup.py --dry-run
```

## 🛠️ Troubleshooting
| Issue | Fix |
|-------|-----|
| "Command not found" | Run `brew doctor` and fix warnings |
| Python version mismatch | Use `python3` explicitly |
| Permission denied | `chmod +x radarr_cleanup.py` |

[Back to Main README](../README.md)