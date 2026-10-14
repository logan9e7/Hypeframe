"""Manual free-quota-aware YouTube discovery; prints candidates for review, never publishes.

Run from backend: python -m scripts.discover_videos --anime Naruto --moment Rasengan
Requires YOUTUBE_API_KEY environment variable.
"""
import argparse
import json
from app.video_discovery import discover_candidates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--anime', required=True)
    parser.add_argument('--moment', required=True)
    parser.add_argument('--limit', type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(discover_candidates(args.anime, args.moment, args.limit), indent=2))

if __name__ == '__main__':
    main()
