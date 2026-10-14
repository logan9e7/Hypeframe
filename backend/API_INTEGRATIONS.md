# Hypeframe free API integrations

## Available endpoints

- `GET /api/anime/search?q=Naruto&provider=all&limit=5`: searches Jikan, AniList and Kitsu, normalizes the responses, caches per process for 24 hours and tolerates individual provider outages.
- `GET /api/anime/search?q=Bleach&provider=anilist`: restricts search to one provider.
- `POST /api/video-submissions`: accepts a YouTube URL for an existing curated moment, holds it for moderation.
- `GET /api/moments`: curated moments.

## YouTube discovery (API key required)

Run `cd backend && YOUTUBE_API_KEY=... python -m scripts.discover_videos --anime Naruto --moment Rasengan`. Results are **candidates**; no automated publishing. Configure `YOUTUBE_API_KEY` privately in the backend environment, never in `NEXT_PUBLIC_*` or Git.

## Provider notes

- Jikan v4: no key, unofficial MyAnimeList-derived metadata, respect 3 requests/sec and 60/min.
- AniList GraphQL: no key for public catalog queries, currently may throttle to 30 requests/min. Respect commercial usage terms.
- Kitsu JSON:API: no key for public anime catalog searches, may be unavailable or change.
- YouTube Data API v3: key needed for search and video detail checks; daily quotas. Official embed links only; embeddable does not prove content rights.
- No API here grants rights to host anime episodes or copyrighted clips.

## Operational constraints

- The per-process cache and throttling are for a small MVP; multiple Render instances need shared limits/cache.
- External APIs can fail or change their terms. Do not rely on all providers being available.
- This is catalog lookup, not automatic catalog ingestion or clip publication.
- The SQLite file on Render free is ephemeral; switch to persistent PostgreSQL before accepting real community content.
- Never enable public discovery/search writes without admin authentication, a shared rate limiter and a moderation queue.
