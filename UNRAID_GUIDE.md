# Unraid Installation & Usage Guide

## 🐳 Unraid-specific Considerations

### Critical Requirements
1. Radarr must be running in Docker
2. Enable "Host access to custom networks" in Docker settings
3. Use privileged mode for Docker container

## 🛠️ Setup Steps

1. **Install Python** (via NerdPack):
   - Go to Plugins → Install NerdPack
   - Enable Python 3.12
   - Click "Apply"

2. **Create persistent scripts directory**:
   ```bash
   mkdir -p /mnt/user/appdata/radarr_cleanup/scripts
   ```

3. **Install requirements**:
   ```bash
   python3 -m pip install requests --user
   ```

4. **Create config.json**:
   ```bash
   nano /mnt/user/appdata/radarr_cleanup/config.json
   ```
   ```json
   {
     "radarr_ip": "radarr",  # Use Docker container name
     "radarr_port": "7878",
     "radarr_api_key": "YOUR_KEY_HERE"
   }
   ```

5. **Download script**:
   ```bash
   wget -P /mnt/user/appdata/radarr_cleanup/scripts https://raw.githubusercontent.com/bizzkoot/radarr_cleanup/main/radarr_cleanup.py
   ```

## 🚀 Scheduled Execution
1. Create new User Script:
   ```bash
   #!/bin/bash
   cd /mnt/user/appdata/radarr_cleanup/scripts
   python3 radarr_cleanup.py --dry-run  # Test first!
   ```

2. Schedule via CA User Scripts plugin

## ⚠️ Limitations
- Script must run on Unraid host (not in container)
- Paths must match Docker volume mappings
- API access requires proper network configuration

## 🔍 Troubleshooting
| Issue | Solution |
|-------|----------|
| Connection refused | Check Docker network mode (bridge/host) |
| Permission denied | `chmod -R 777 /mnt/user/appdata/radarr_cleanup` |
| Missing dependencies | Reinstall NerdPack Python |

[Back to Main README](../README.md)
