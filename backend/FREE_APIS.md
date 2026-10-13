# Free anime and video data sources

| Provider | Purpose | Caveats |
|---|---|---|
| YouTube Data API v3 | Discover official video candidates, verify public/embeddable videos | API key, daily quota; embeds are not automatically authorized uploads |
| Jikan v4 | Anime titles, episode counts, MAL metadata | Unofficial MAL API; 3 requests/second, 60/minute; cache and attribute |
| AniList GraphQL | Anime metadata, tags, series information | Terms restrict bulk collection, competitive use, and some commercial use; respect limits |
| Kitsu JSON:API (kitsu.io/api/edge) | Alternate anime metadata | Verify availability, license and terms before production use |
| YouTube iframe embed | Play approved videos | No video hosting cost; some embeds unavailable by region or rights |

No free metadata API provides licensed clips for every anime moment. Avoid unofficial video scrapers and copyrighted clip mirroring.

The backend includes `search_jikan_anime` for optional enrichment, and `discover_candidates` for key-based YouTube discovery. Neither is an automatic bulk scraper or publication pipeline.
