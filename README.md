# Hypeframe

**Cinematic anime moments archive and community** built with Next.js 15, React 19, TypeScript, FastAPI and Supabase.

**Live website:** https://hypeframe-web.netlify.app  
**Backend API:** https://hypeframe-api.onrender.com/docs  
**Source code:** https://github.com/logan9e7/Hypeframe

## Current status (October 14, 2026)

| Component | Implementation | Production verification |
|---|---|---|
| Cinematic homepage and 12 curated moments | Complete | Netlify deployment of earlier commit is ready |
| Search, filters, spoiler toggle | Complete | Browser behavior not retested this release |
| Saved moments and hype votes | Browser-local only | Not synchronized between users |
| FastAPI /health and moments endpoints | Complete | Render reports deployment live; direct HTTP checks unavailable |
| Anime metadata: Jikan, AniList, Kitsu | Backend integration complete | Live upstream responses not verified |
| YouTube discovery | API-key-based candidate search script | Requires `YOUTUBE_API_KEY`, candidates need moderation |
| Supabase passwordless email login | Implemented in repository | Latest frontend deployment not yet verified |
| Authenticated YouTube link submissions | Supabase browser client with RLS | Requires successful new frontend deployment and email test |
| Comment database | Created, RLS enabled | Comment UI not implemented |
| Moderator dashboard | Not implemented | — |

**Important:** The latest confirmed Netlify published deploy was commit `c6f419f`, before the authentication changes. A new deploy must complete before the login and authenticated submissions are available on the public site.

## Local setup

Requires Node.js 20+ and Python 3.11+.

```bash
npm install
npm run dev
```

Create `.env.local`:

```dotenv
NEXT_PUBLIC_API_URL=https://hypeframe-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://doyyradsaigmrvlabwhg.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=<your Supabase publishable key>
```

Get the publishable key from Supabase Dashboard → Project Settings → API Keys. **Never put a service role or secret key in a `NEXT_PUBLIC_*` variable.** The publishable key is designed for browser use.

Run the API locally:

```bash
cd backend
python -m venv .venv
# Activate .venv for your operating system
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
```

See [backend/README.md](backend/README.md), [backend/API_INTEGRATIONS.md](backend/API_INTEGRATIONS.md), and [backend/VIDEO_PIPELINE.md](backend/VIDEO_PIPELINE.md).

## Authentication and community submissions

- Login: https://hypeframe-web.netlify.app/login
- Submit clip: https://hypeframe-web.netlify.app/submit
- Supabase project: https://supabase.com/dashboard/project/doyyradsaigmrvlabwhg
- Configure **Site URL** `https://hypeframe-web.netlify.app` and allow redirect `https://hypeframe-web.netlify.app/auth/callback` under Authentication → URL Configuration.
- Email sign-in is passwordless. New users may need to confirm email before participating.
- Users may insert their own `pending_review` submissions; approval is reserved for future moderator tooling.
- Comments are stored in a separate RLS-protected table, but the frontend discussion UI is not yet shipped.
- No copyrighted anime video is uploaded or hosted.

## Free API integrations

| API | Use | Requirement |
|---|---|---|
| Jikan v4 | Anime metadata | Public API; obey limits |
| AniList GraphQL | Anime metadata | Public API; obey usage terms |
| Kitsu JSON:API | Anime metadata | Public API; availability varies |
| YouTube Data API v3 | Find public, embeddable video candidates | `YOUTUBE_API_KEY` and quota |

`GET /api/anime/search?q=Naruto&provider=all&limit=5` searches the three metadata providers and caches results for 24 hours in-process. An upstream provider may be unavailable. The API does **not** automatically import videos or approve third-party uploads.

Run discovery with:

```bash
cd backend
YOUTUBE_API_KEY=your_key python -m scripts.discover_videos --anime Naruto --moment Rasengan
```

Set the YouTube key in Render's environment settings, never in GitHub or a browser variable.

## Deployment

- Frontend: Netlify project `hypeframe-web`, GitHub `main` branch.
- Backend: Render service `hypeframe-api`, free tier.
- Community data: Supabase project `Hypeframe`, Mumbai (`ap-south-1`).
- Netlify build environment must include `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`.
- After any environment change, deploy the current GitHub commit and confirm the published commit SHA in Netlify.
- Check `/login`, email link callback, `/submit`, and a real authenticated insert; dashboard "ready" alone does not prove the auth flow works.

## Security and limitations

Supabase `video_submissions` and `moment_comments` have RLS enabled. Browser clients use only a publishable key. Supabase is the durable store for the new authenticated submissions; the older FastAPI anonymous submission endpoint still uses **ephemeral SQLite** and must not be treated as the production submission path. Do not expose that legacy endpoint for public production use without authentication and rate limiting.

Render free services may sleep and take time to wake. No paid services are required, but all free services have quotas. No API grants permission to redistribute copyrighted anime footage.

## Developer checks

```bash
npm run typecheck
npm run build
cd backend
pytest -q
```

These commands should be run in CI for the new auth release; the latest auth build and browser email sign-in have not been independently verified here.
