# Trend research mode (scraped data)

Use this when the user asks what's trending or what songs edits use right now, or when no user references exist yet. If the user has sent references, those override everything here.

## Ranking
- **Recent beats all-time.** Rank by views/day for posts 60 days old or newer (weight posts 30 days old or newer highest), and mark each sound rising/current/stale by its newest use. Old giants and old sounds (TAKI RUMBA, MONTAGEM ALQUIMIA, Meant To Be) count as stale for this user.
- Find outliers by account: list the authors of recent hits with `fetch_tiktok.py <handle> --pool 40` (no login, safe in parallel) and keep posts at 3x or more the account median.

## Collecting
1. TikTok search needs the logged-in scraper profile: run `tt_login.py` once (the user logs in to a visible window), then `tt_search.py out.json "q1" "q2" ... --scrolls 8 --headed` (social-viral-analyzer scripts). Only one agent may use that profile at a time.
2. Filter results to the anime with a regex on desc/music, and add `age_days` and `views_per_day`.
3. 60-75% of anime edits say "original sound". Identify the song from TikTok's matched-song metadata on the video page first, then Shazam. Shazam rate-limits when several agents share an IP, so cap lookups per agent and use the signature-plus-urllib workaround in social-viral-analyzer `references/music-identification.md`.

## What the data showed (use as context, not rules)
- Hype/shonen: episode-day posting wins (most hype outliers went up on the day the episode aired). The edit the user liked from data-driven work was a Black Clover S2 "PEAK:" label edit: a hoodtrap sound with the drop within 2 s, 2-beat cuts, a bright magenta grade, a small persistent label, 18-19 s, and a clean bar-aligned loop.
- Small accounts break out often, so a fresh account is not a blocker.
- Data-driven romance edits (scraped "rising" sounds, subtitle hooks, slow lyric-phrase cuts) were rejected by the user even after model critics scored them 8/10. For romance, always work from user references.
