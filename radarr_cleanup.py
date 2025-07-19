import requests
import json
import argparse
from datetime import datetime
from pathlib import Path

def get_log_path():
    """Get platform-appropriate log file path"""
    import platform
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        log_dir = home / "AppData" / "Local" / "RadarrCleanup"
    elif system == "Darwin":
        log_dir = home / "Library" / "Logs" / "RadarrCleanup"
    else:  # Linux/BSD
        log_dir = home / ".radarr_cleanup" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "radarr_cleanup.log"

# Load config with validation and error handling
try:
    with open('config.json') as f:
        config = json.load(f)
    
    # Validate required fields
    required_keys = ['radarr_ip', 'radarr_port', 'radarr_api_key']
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required config key: {key}")
        if config[key] == "YOUR_API_KEY_HERE" and key == "radarr_api_key":
            raise ValueError("Please replace 'YOUR_API_KEY_HERE' with your actual Radarr API key in config.json")
    
    RADARR_URL = f"http://{config['radarr_ip']}:{config['radarr_port']}"
    API_KEY = config['radarr_api_key']
    HEADERS = {"X-Api-Key": API_KEY}

except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
    print(f"Configuration error: {e}")
    print("Please check your config.json file and try again.")
    exit(1)

def get_movies():
    """Fetch all movies from Radarr"""
    try:
        response = requests.get(f"{RADARR_URL}/api/v3/movie", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch movies: {e}")
        exit(1)

def delete_movie(movie_id):
    """Delete a movie from Radarr"""
    try:
        response = requests.delete(f"{RADARR_URL}/api/v3/movie/{movie_id}", headers=HEADERS)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to delete movie: {e}")
        return False

def parse_selection(selection, movies):
    """Parse user's selection of movies to keep"""
    kept_indices = []
    for item in selection:
        item = item.strip()
        if item.isdigit():
            index = int(item) - 1
            if 0 <= index < len(movies):
                kept_indices.append(index)
        else:
            for i, movie in enumerate(movies):
                if item.lower() in movie['title'].lower():
                    kept_indices.append(i)
    return list(set(kept_indices))

def verify_deletions(movie_ids):
    """Verify movies were actually removed"""
    try:
        remaining = requests.get(f"{RADARR_URL}/api/v3/movie", headers=HEADERS).json()
        remaining_ids = {m['id'] for m in remaining}
        return len(set(movie_ids) - remaining_ids)
    except requests.exceptions.RequestException as e:
        print(f"Verification failed: {e}")
        return 0

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Radarr Movie Cleanup Tool')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate deletion without making changes')
    args = parser.parse_args()

    # Prompt for runtime threshold
    max_runtime = int(input("Enter the maximum runtime in minutes: "))

    # Fetch movies
    movies = get_movies()
    
    # Filter and display
    short_movies = [m for m in movies if m['runtime'] < max_runtime]
    print(f"\nFound {len(short_movies)} movies under {max_runtime} minutes:")
    for i, movie in enumerate(short_movies):
        print(f"[{i+1}] {movie['title']} ({movie['year']}) - {movie['runtime']}min")
    
    # Early exit if no movies found
    if not short_movies:
        print("No movies to delete.")
        exit()

    # User choice: delete all or select?
    delete_all = input("\nDelete ALL these movies? (y/n): ").strip().lower()
    if delete_all == 'y':
        to_delete = short_movies
    else:
        # User selection: which movies to keep
        keep = input("\nEnter numbers/titles to KEEP (comma-separated): ").strip().split(',')
        kept_indices = parse_selection(keep, short_movies)
        to_delete = [m for i, m in enumerate(short_movies) if i not in kept_indices]
    
    # Confirmation
    print("\nMOVIES TO DELETE:")
    for i, movie in enumerate(to_delete):
        print(f"{i+1}. {movie['title']}")
    if not to_delete:
        print("No movies selected for deletion. Exiting.")
        exit()
    if input("Confirm deletion? (y/n): ").lower() != 'y':
        exit()
    
    # Delete movies with dry-run support
    for movie in to_delete:
        if args.dry_run:
            print(f"[DRY RUN] Would delete {movie['title']}")
        else:
            delete_movie(movie['id'])
    
    # Verification and logging
    log_file = get_log_path()
    with log_file.open('a') as f:
        f.write(f"Deletion initiated at {datetime.now()}\n")
        f.write(f"Movies deleted: {len(to_delete)}\n")
    
    verify_deletions([m['id'] for m in to_delete])

if __name__ == "__main__":
    main()
