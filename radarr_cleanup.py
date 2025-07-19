import requests
import json
import argparse
import shutil
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

def add_import_exclusion(movie):
    """Add movie to Radarr's import exclusion list"""
    payload = {
        "tmdbId": movie['tmdbId'],
        "movieTitle": movie['title'],
        "movieYear": movie['year']
    }
    try:
        response = requests.post(
            f"{RADARR_URL}/api/v3/importlistexclusion",
            json=payload,
            headers=HEADERS
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to add exclusion for {movie['title']}: {e}")
        return False

def parse_selection(selection, movies, prefix=''):
    """Parse user's selection of movies to keep with optional prefix"""
    kept_indices = []
    prefix_len = len(prefix)
    
    for item in selection:
        item = item.strip()
        if item.startswith(prefix) and item[prefix_len:].isdigit():
            # Handle prefixed indices (like Z1, Z2)
            index = int(item[prefix_len:]) - 1
            if 0 <= index < len(movies):
                kept_indices.append(index)
        elif item.isdigit():
            # Handle regular indices
            index = int(item) - 1
            if 0 <= index < len(movies):
                kept_indices.append(index)
        else:
            # Handle title matches
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

    # Prompt for runtime threshold with validation
    while True:
        try:
            input_str = input("Enter the maximum runtime in minutes: ").strip()
            if not input_str:
                raise ValueError("Input cannot be empty")
            max_runtime = int(input_str)
            if max_runtime <= 0:
                raise ValueError("Runtime must be a positive number")
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid number.")

    # Fetch movies
    movies = get_movies()
    
    # Filter movies under threshold
    short_movies = [m for m in movies if m['runtime'] < max_runtime]
    
    # Separate 0min movies
    zero_runtime = [m for m in short_movies if m['runtime'] == 0]
    valid_short = [m for m in short_movies if m['runtime'] > 0]
    
    # Handle 0min movies first
    zero_to_delete = []
    if zero_runtime:
        print(f"\nFound {len(zero_runtime)} movies with 0min runtime (possible metadata errors):")
        for i, movie in enumerate(zero_runtime):
            print(f"[Z{i+1}] {movie['title']} ({movie['year']})")
        
        review_zero = input("\nReview these 0min movies? (y/n): ").strip().lower()
        if review_zero == 'y':
            # User selection for 0min movies (ask for deletion instead of keep)
            delete_zero = input("\nEnter Z-numbers/titles to DELETE (comma-separated): ").strip().split(',')
            delete_zero_indices = parse_selection(delete_zero, zero_runtime, prefix='Z')
            zero_to_delete = [zero_runtime[i] for i in delete_zero_indices]
            
            # Confirmation for 0min deletion
            if zero_to_delete:
                print("\n0min MOVIES TO DELETE:")
                for i, movie in enumerate(zero_to_delete):
                    print(f"Z{i+1}. {movie['title']}")
                if input("Confirm deletion of these 0min movies? (y/n): ").lower() != 'y':
                    zero_to_delete = []
    
    # Handle valid short movies
    to_delete = []
    if valid_short:
        print(f"\nFound {len(valid_short)} movies under {max_runtime} minutes (excluding 0min):")
        for i, movie in enumerate(valid_short):
            print(f"[{i+1}] {movie['title']} ({movie['year']}) - {movie['runtime']}min")
        
        # User choice: delete all or select?
        delete_all = input("\nDelete ALL these movies? (y/n): ").strip().lower()
        if delete_all == 'y':
            to_delete = valid_short
        else:
            # User selection: which movies to keep
            keep = input("\nEnter numbers/titles to KEEP (comma-separated): ").strip().split(',')
            kept_indices = parse_selection(keep, valid_short)
            to_delete = [m for i, m in enumerate(valid_short) if i not in kept_indices]
    
    # Combine deletion lists
    to_delete += zero_to_delete
    
    # Early exit if no movies to delete
    if not to_delete:
        print("No movies selected for deletion. Exiting.")
        exit()
    
    # Confirmation for all deletions
    print("\nFINAL MOVIES TO DELETE:")
    for i, movie in enumerate(to_delete):
        if movie in zero_to_delete:
            print(f"Z{i+1}. {movie['title']} (0min)")
        else:
            print(f"{i+1}. {movie['title']} ({movie['runtime']}min)")
    
    if input("\nConfirm deletion of ALL listed movies? (y/n): ").lower() != 'y':
        exit()
    
    # Delete movies with dry-run support
    for movie in to_delete:
        if args.dry_run:
            print(f"[DRY RUN] Would delete {movie['title']}")
        else:
            delete_movie(movie['id'])

    # Disk space reclaim reporting
    import os
    total, used, free = shutil.disk_usage("/")
    print("Disk Space : ")
    print("Total: %d GiB" % (total // (2**30)))
    print("Used: %d GiB" % (used // (2**30)))
    print("Free: %d GiB" % (free // (2**30)))
    
    # Verification and logging
    log_file = get_log_path()
    with log_file.open('a') as f:
        f.write(f"Deletion initiated at {datetime.now()}\n")
        f.write(f"Movies deleted: {len(to_delete)}\n")
        f.write("Total: %d GiB" % (total // (2**30)))
        f.write("Used: %d GiB" % (used // (2**30)))
        f.write("Free: %d GiB" % (free // (2**30)))
    
    verify_deletions([m['id'] for m in to_delete])
    
    # Import exclusion option
    exclusion_choice = input("\nAdd these movies to import exclusion to prevent re-adding? (y/n): ").strip().lower() == 'y'
    if exclusion_choice:
        if args.dry_run:
            print(f"[DRY RUN] Would add {len(to_delete)} movies to import exclusion list")
        else:
            print("Adding movies to import exclusion list...")
            for movie in to_delete:
                if add_import_exclusion(movie):
                    print(f"Added {movie['title']} to import exclusion list")
                else:
                    print(f"Failed to add {movie['title']} to import exclusion list")
            print("Import exclusion process completed")

if __name__ == "__main__":
    main()
