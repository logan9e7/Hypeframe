"""Free anime catalog enrichment; no API key needed. Metadata is not clip licensing."""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def search_jikan_anime(title: str, limit: int = 5) -> list[dict]:
    if not 1 <= len(title.strip()) <= 100:
        raise ValueError('Title length must be 1-100')
    params = urlencode({'q': title, 'limit': min(max(limit, 1), 10), 'sfw': 'true'})
    req = Request('https://api.jikan.moe/v4/anime?' + params, headers={'User-Agent': 'Hypeframe/0.1'})
    with urlopen(req, timeout=8) as response:
        payload = json.load(response)
    return [{'mal_id': row['mal_id'], 'title': row.get('title_english') or row.get('title'), 'episodes': row.get('episodes'), 'url': row.get('url')} for row in payload.get('data', [])]
