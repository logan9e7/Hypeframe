"""Free anime metadata providers with bounded queries and in-process caching.

All calls originate from fixed trusted API endpoints, never user-supplied URLs.
Provider outages fail independently. No paid service required.
"""
import json
import time
from threading import Lock
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ANILIST_QUERY = """query ($search: String, $perPage: Int) {
 Page(page: 1, perPage: $perPage) {
  media(search: $search, type: ANIME, isAdult: false) {
   id title { romaji english native } episodes seasonYear
   siteUrl coverImage { medium }
  }
 }
}"""

_CACHE: dict[tuple[str, str, int], tuple[float, list[dict]]] = {}
_LOCK = Lock()
TTL_SECONDS = 86400

def _json_request(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    headers = {'User-Agent': 'Hypeframe/0.1 (anime metadata)', 'Accept': 'application/json'}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    req = Request(url, data=data, headers=headers, method='POST' if data is not None else 'GET')
    with urlopen(req, timeout=8) as response:
        return json.load(response)

def _search_jikan(title: str, limit: int) -> list[dict]:
    params = urlencode({'q': title, 'limit': limit, 'sfw': 'true'})
    data = _json_request('https://api.jikan.moe/v4/anime?' + params)
    return [{'source': 'jikan', 'id': str(x['mal_id']), 'title': x.get('title_english') or x.get('title') or '',
             'episodes': x.get('episodes'), 'url': x.get('url'), 'image': (x.get('images') or {}).get('jpg', {}).get('image_url')}
            for x in data.get('data', [])]

def _search_anilist(title: str, limit: int) -> list[dict]:
    data = _json_request('https://graphql.anilist.co', {'query': ANILIST_QUERY, 'variables': {'search': title, 'perPage': limit}})
    if data.get('errors'):
        raise ValueError('AniList API returned errors')
    items = ((data.get('data') or {}).get('Page') or {}).get('media') or []
    return [{'source': 'anilist', 'id': str(x['id']), 'title': x['title'].get('english') or x['title'].get('romaji') or '',
             'episodes': x.get('episodes'), 'url': x.get('siteUrl'), 'image': (x.get('coverImage') or {}).get('medium')}
            for x in items]

def _search_kitsu(title: str, limit: int) -> list[dict]:
    params = urlencode({'filter[text]': title, 'page[limit]': limit})
    data = _json_request('https://kitsu.io/api/edge/anime?' + params)
    out = []
    for x in data.get('data', []):
        a = x.get('attributes') or {}
        out.append({'source': 'kitsu', 'id': str(x['id']), 'title': a.get('canonicalTitle') or '',
                    'episodes': a.get('episodeCount'), 'url': 'https://kitsu.io/anime/' + str(x['id']),
                    'image': (a.get('posterImage') or {}).get('small')})
    return out

_PROVIDERS = {'jikan': _search_jikan, 'anilist': _search_anilist, 'kitsu': _search_kitsu}

def search_metadata(title: str, provider: str = 'all', limit: int = 5) -> dict:
    title = title.strip()
    if not 2 <= len(title) <= 100:
        raise ValueError('Title must be 2-100 characters')
    if provider != 'all' and provider not in _PROVIDERS:
        raise ValueError('Unknown metadata provider')
    limit = min(max(limit, 1), 10)
    results: list[dict] = []
    errors: list[str] = []
    for name in (_PROVIDERS if provider == 'all' else [provider]):
        key = (name, title.casefold(), limit)
        with _LOCK:
            cached = _CACHE.get(key)
        if cached and cached[0] > time.monotonic():
            results.extend(cached[1])
            continue
        try:
            found = _PROVIDERS[name](title, limit)
            with _LOCK:
                if len(_CACHE) > 500:
                    _CACHE.clear()
                _CACHE[key] = (time.monotonic() + TTL_SECONDS, found)
            results.extend(found)
        except (OSError, ValueError, KeyError, TypeError, TimeoutError):
            errors.append(name)
    return {'results': results, 'unavailable_providers': errors}
