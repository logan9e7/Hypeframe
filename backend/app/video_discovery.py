"""Safe YouTube video discovery. Search requires an optional user-provided API key.
No downloading or rehosting copyrighted video files.
"""
import os
import re
import json
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import urlopen, Request

VIDEO_ID = re.compile(r'^[A-Za-z0-9_-]{11}$')

def parse_youtube_id(url: str) -> str | None:
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or '').lower()
        if host in ('youtu.be', 'www.youtu.be'):
            candidate = parsed.path.strip('/').split('/')[0]
        elif host in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            if parsed.path == '/watch':
                candidate = parse_qs(parsed.query).get('v', [''])[0]
            elif parsed.path.startswith(('/shorts/', '/embed/', '/live/')):
                candidate = parsed.path.split('/')[2]
            else:
                return None
        else:
            return None
        return candidate if VIDEO_ID.fullmatch(candidate) else None
    except (ValueError, IndexError):
        return None

def _youtube_api(endpoint: str, params: dict) -> dict:
    key = os.getenv('YOUTUBE_API_KEY')
    if not key:
        raise RuntimeError('YOUTUBE_API_KEY not configured')
    query = urlencode({**params, 'key': key})
    req = Request(f'https://www.googleapis.com/youtube/v3/{endpoint}?{query}', headers={'User-Agent': 'Hypeframe/0.1'})
    with urlopen(req, timeout=12) as response:
        return json.load(response)

def discover_candidates(anime: str, moment: str, limit: int = 5) -> list[dict]:
    """Discover candidates; results must be reviewed before publishing."""
    limit = min(max(limit, 1), 10)
    search = _youtube_api('search', {'part': 'snippet', 'q': f'{anime} {moment} official anime clip', 'type': 'video', 'maxResults': limit, 'videoEmbeddable': 'true', 'safeSearch': 'moderate'})
    ids = [item.get('id', {}).get('videoId') for item in search.get('items', [])]
    ids = [id for id in ids if id and VIDEO_ID.fullmatch(id)]
    if not ids:
        return []
    details = _youtube_api('videos', {'part': 'snippet,status', 'id': ','.join(ids)})
    results = []
    for item in details.get('items', []):
        status = item.get('status', {})
        if status.get('embeddable') is not True or status.get('privacyStatus') != 'public':
            continue
        snippet = item.get('snippet', {})
        results.append({'video_id': item['id'], 'url': f'https://www.youtube.com/watch?v={item["id"]}', 'title': snippet.get('title', ''), 'channel': snippet.get('channelTitle', ''), 'channel_id': snippet.get('channelId', ''), 'status': 'pending_review'})
    return results
