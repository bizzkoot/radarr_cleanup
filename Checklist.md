# Radarr Movie Cleanup Script

## Overview
A CLI tool to delete movies from Radarr based on runtime criteria, with user confirmation and safety checks.

## Requirements
- Python 3.8+
- `requests` library (`pip install requests`)
- Radarr instance (v4+)

## Configuration
Create `config.json` with:
```json
{
  "radarr_ip": "YOUR_RADARR_IP",
  "radarr_port": "YOUR_RADARR_PORT",
  "radarr_api_key": "YOUR_API_KEY",
  "max_runtime_minutes": 120
}
```

## Workflow

### 1. Fetch Movies from Radarr
- **API Endpoint**: `GET /api/v3/movie`
- **Headers**: 
  ```python
  headers = {"X-Api-Key": API_KEY}
  ```
- **Process**: 
  ```python
  response = requests.get(f"http://{IP}:{PORT}/api/v3/movie", headers=headers)
  ```

### 2. Filter Movies by Runtime
```python
eligible_movies = [m for m in movies if m.get('runtime', 0) > MAX_RUNTIME]
```

### 3. Display Movies
Format:
```
[Index] Title (Year) - Runtime: X minutes
```

### 4. User Selection
- Prompt: 
  ```
  Enter numbers/titles to KEEP (comma-separated): 
  ```
- Process:
  ```python
  kept_input = input().strip().split(',')
  ```

### 5. Deletion Confirmation
- Show:
  ```
  MOVIES TO DELETE:
  [1] Movie A (120min)
  [2] Movie B (130min)
  Confirm deletion? (y/n): 
  ```

### 6. Delete Movies & Files
- **API Endpoint**: `DELETE /api/v3/movie/{id}?deleteFiles=true`
- **Process**:
  ```python
  for movie in to_delete:
      requests.delete(f"http://{IP}:{PORT}/api/v3/movie/{movie['id']}?deleteFiles=true&addImportExclusion=true", headers=headers)
  ```

### 7. Verify Deletion
1. Check blocklist: `GET /api/v3/blocklist`
2. Validate no trace in movie list

### 8. Final Report
```
Deleted 5 movies:
- Movie A (blocklisted: ✅)
- Movie B (blocklisted: ✅)
Disk space freed: 42.5 GB
```

## Error Handling
- Validate API connection
- Check HTTP responses
- User input sanitization

## Sample Script
```python
import requests
import json

# Load config
with open('config.json') as f:
    config = json.load(f)

RADARR_URL = f"http://{config['radarr_ip']}:{config['radarr_port']}"
API_KEY = config['radarr_api_key']
MAX_RUNTIME = config['max_runtime_minutes']
HEADERS = {"X-Api-Key": API_KEY}

def main():
    # Fetch movies
    movies = get_movies()
    
    # Filter and display
    long_movies = [m for m in movies if m['runtime'] > MAX_RUNTIME]
    print("\nMOVIES EXCEEDING RUNTIME:")
    for i, movie in enumerate(long_movies):
        print(f"[{i+1}] {movie['title']} ({movie['year']}) - {movie['runtime']}min")
    
    # User selection
    keep = input("\nEnter numbers/titles to KEEP (comma-separated): ").strip().split(',')
    kept_indices = parse_selection(keep, long_movies)
    
    # Prepare deletion list
    to_delete = [m for i, m in enumerate(long_movies) if i not in kept_indices]
    
    # Confirmation
    print("\nMOVIES TO DELETE:")
    [print(f"{i+1}. {m['title']}") for i, m in enumerate(to_delete)]
    if input("Confirm deletion? (y/n): ").lower() != 'y':
        exit()
    
    # Delete movies
    for movie in to_delete:
        delete_movie(movie['id'])
    
    # Verification
    verify_deletions([m['id'] for m in to_delete])

if __name__ == "__main__":
    main()
```

## Functions to Implement
- `get_movies()`: Fetch movies from Radarr
- `parse_selection()`: Convert user input to indices
- `delete_movie(movie_id)`: Delete with blocklist flag
- `verify_deletions(movie_ids)`: Check blocklist and movie list

## Post-Execution
1. Script outputs deletion summary
2. Logs written to `radarr_cleanup.log`
```

## How to Use This in Your IDE:
1. Create a new project
2. Save this as `README.md`
3. Implement the functions using the workflow
4. Create `config.json` with your details
5. Run with `python radarr_cleanup.py`

> **Warning**: Deletion is permanent! Test with dummy data first. Add `--dry-run` flag during development.