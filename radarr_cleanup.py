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

# Load config using pathlib for cross-platform compatibility
with open('config.json') as f:
    config = json.load(f)

RADARR_URL = f"http://{config['radarr_ip']}:{config['radarr_port']}"
API_KEY = config['radarr_api_key']
MAX_RUNTIME = config['max_runtime_minutes']
HEADERS = {"X-Api-Key": API_KEY}

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Radarr Movie Cleanup Tool')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate deletion without making changes')
    args = parser.parse_args()

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