# macOS Installation & Usage Guide

## 🍎 Step-by-Step Setup

1. **Install Homebrew**  
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**  
   ```bash
   brew install python
   echo 'export PATH="/opt/homebrew/opt/python/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Create Project Folder**
   ```bash
   mkdir -p ~/radarr_cleanup
   cd ~/radarr_cleanup
   ```

4. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Required Package**
   ```bash
   python3 -m pip install requests
   ```

6. **Create Configuration File**
   ```bash
   nano config.json
   ```
   Paste:
   ```json
   {
     "radarr_ip": "localhost",
     "radarr_port": "7878",
     "radarr_api_key": "YOUR_API_KEY_HERE"  // Replace with your actual API key
   }
   ```
   ^O to save, ^X to exit
   ⚠️ IMPORTANT: Replace "YOUR_API_KEY_HERE" with your actual Radarr API key

7. **Download Script**
   ```bash
   curl -O https://raw.githubusercontent.com/bizzkoot/radarr_cleanup/main/radarr_cleanup.py
   ```

## 🏃 Running the Script
```bash
# Navigate to the project folder
cd ~/radarr_cleanup

# Activate the virtual environment
source venv/bin/activate

# Normal mode
python3 radarr_cleanup.py

# Dry-run mode (safe test)
python3 radarr_cleanup.py --dry-run
```

## 🛠️ Troubleshooting
| Issue | Fix |
|-------|-----|
| "Command not found" | Run `brew doctor` and fix warnings |
| "source: no such file or directory: venv/bin/activate" | Ensure you're in the same directory where you created the virtual environment |
| JSONDecodeError: Expecting value | Ensure you've replaced "YOUR_API_KEY_HERE" with your actual API key in config.json |
| Python version mismatch | Use `python3` explicitly |
| Permission denied | `chmod +x radarr_cleanup.py` |
| ModuleNotFoundError: No module named 'requests' | Ensure `requests` is installed in the correct Python environment using `python3 -m pip install requests` |

[Back to Main README](../README.md)
