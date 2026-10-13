# Video discovery and community submission plan

## Cost and compliance

- Use official YouTube Data API v3 with your own optional `YOUTUBE_API_KEY`. It has a limited free daily quota; search requests consume substantially more quota than metadata lookups. Check current quotas in Google Cloud before enabling scheduled discovery.
- YouTube's `videoEmbeddable` search filter and `status.embeddable` metadata help identify playable videos but **do not prove uploader authorization**.
- Keep an allowlist of official anime distributor / studio channels, curated and reviewed by a moderator. Do not automatically approve arbitrary videos just because they are embeddable.
- Never download or mirror third-party anime video files without appropriate rights.

## Discovery flow

1. Start with curated moment metadata in the database.
2. For each moment, query `discover_candidates(anime, title)` (optional YouTube API key).
3. Deduplicate by `video_id` and save candidates as `pending_review` in persistent PostgreSQL.
4. Verify source channel, episode match, region/playability, and appropriateness.
5. Publish approved video IDs as official embeds on moment pages.
6. Let signed-in members submit YouTube links to the same moderation queue; apply rate limiting and report controls.

## Security

The discovery module does not fetch arbitrary user-supplied URLs. It parses video IDs from approved YouTube hostnames and calls the official Google API. Do not create public moderation or publishing endpoints without authentication and role checks.

## Not implemented yet

Persistent candidate queue, API credentials, scheduled discovery, member submission endpoints, moderator dashboard, and embedded video player. These require database setup and an authenticated workflow.
