# Identify a creator's background music

Use this when the user asks "what bg music does <creator> use", "find music from their videos that fits mine", or wants music that is on-trend for a niche.

## Quick path: one reel the user sends ("find the music in this reel")
1. `yt-dlp -o "ref.%(ext)s" --write-info-json <reel url>` downloads a public IG reel without a login. `info.json` usually has no track or artist tag, because the music is baked into the original audio.
2. Cut raw 12 s mono 16 kHz windows every ~8 s: `ffmpeg -nostdin -ss $s -t 12 -i ref.mp4 -ac 1 -ar 16000 w_$s.wav`.
3. Run `Shazam().recognize` on each window in sequence, with a 3 s gap and `asyncio.wait_for(…, 30)` (venv: `uv venv shz -p 3.11 && uv pip install -p shz shazamio`; on the PC the social-scraper venv already has shazamio). A music bed under a voice often matches on the raw mix. Only add demucs (step 2 below) if no window hits.
4. Confident = 2-3+ windows on the same track with `offset - window_start` constant (±1.5 s). That constant is where in the song the reel starts. Report the title, the artist, the section, and that he should add it in-app if it's copyrighted.
5. To reuse the same section from a library file, Shazam two 12 s windows of the LOCAL file and compute `local_start - shazam_offset`. Uploads differ in intro length (the YouTube official audio sat +0.37 s from Shazam's master). Start the mix at `reel_offset + shift`. Note the section in the CATALOG row.

## Proven pipeline v2 (talking-head creators; Mino Lee latest 90 → 70 identified, 52 tracks)
Scripts in `scripts/music/` — copy them into a work dir `W` first (they use their own folder as the work dir; `browser_shz.py` hardcodes `D`, edit it). Run them with the social-scraper venv python (needs numpy, scipy, shazamio, playwright; ffmpeg on PATH). `fp.py` reads the music library from `~/PersonalBrandAssets/music` (Mac), so edit `LIB` on the PC.
1. `fetch90.py W --want 115` (scraper venv): scrolls `/reels/`, then `/api/v1/media/<pk>/info/` per reel (owner, date, music tag) and downloads the audio in the same pass. Keep owner==handle or coauthor, sort by `taken_at`, take the N latest.
2. **Remove the voice first**: `demucs --two-stems=vocals -n htdemucs -d mps` (Mac; `-d cuda` on the PC; venv `scratch/dmx`, torch<2.9, not installed on the PC yet: `uv venv` + `uv pip install demucs`) on all reels in ONE call (~15 s/reel). Raw-mix Shazam hit 2 of 25 windows; the `no_vocals` stem hit ~80 %.
3. `sigs90.py W`: local signatures (no network), 12 s windows every 10 s on the stem + 2 raw windows. POST them with `browser_shz.py` from the cloud browser (`run(budget_s=345, gap=1.2)`; browser_exec dies at 420 s, so ~110 lookups per call), or `local_post.py` when the local IP isn't 429'd. Both IPs got 429'd after ~760 lookups; it lifted after ~45 min.
4. Unidentified reels with music: `sigs_rates.py W <ranks>` adds 1.15/0.87/1.07/0.93 rate windows. Check stem loudness first: stem below about -48 LUFS = no background music.
5. `agg.py` → per-reel tracks with window counts. Ignore 1-window hits in a reel where another track has 4+.
6. Download each track with yt-dlp, preferring `<Artist> - Topic` uploads whose duration matches Apple's `trackTimeMillis` (no Apple duration → check the pick by hand: obscure titles returned unrelated videos 5 times).
7. **Verify, two ways** (scripts `fp.py`, `preview_check.py`, then `final.py`):
   - File identity: fingerprint the downloaded file against Apple's 30 s `previewUrl` of the Shazam-matched trackId. Real ≥100 (often 500+), wrong file ≤10. Caught a 432 Hz re-tune and a slowed re-upload.
   - Reel ↔ file: peak-pair fingerprint (`fp.py`) of the reel's music stem vs the full file. Negatives max 6 (median 2); ≥15 and ≥2× second-best offset = match. Quiet beds (stem around -40 LUFS) and sped-up edits often score low even when right, so also accept Shazam 3+ windows whose offsets advance with the window start (±1.5 s).
   - Sung hooks (a chorus as the first 2 s): demucs moves them to `vocals.wav`, so fingerprint that stem too.
   - Don't verify at Shazam's offset in the YouTube file: uploads have different intros. Chroma cross-correlation could not separate real from fake (z 4-5 for both); don't use it.

## Procedure
1. **Pick targets.** Choose their top ~90 reels by outlier plus the ~30 most recent. If a hook-bank or format analysis already exists, take ids and pks from its `list_ig_<handle>.json` or talking table.
2. **Read IG's own music tag first** in the logged-in scraper profile: `fetch('/api/v1/media/<pk>/info/')` → `items[0].clips_metadata`.
   - `music_info.music_asset_info` → `title`, `display_artist`. This is a licensed track picked in-app.
   - `original_sound_info` → `original_audio_title` / `ig_artist.username`. This means "original audio": the music is baked into the creator's own upload, so the title tells you nothing.
   - Talking-head creators are almost all original audio (182 of 192 for one creator), so step 3 is where the real answers come from.
   - Sleep 1.5-2.5 s between calls, and stop on 401/429.
3. **Fingerprint the baked-in music with Shazam.**
   - Setup: `uv venv shz -p 3.11 && uv pip install -p shz shazamio`.
   - Get fresh media: in the SAME Playwright session as step 2, take `video_versions[-1].url`, download it right away, and keep only the audio (`ffmpeg -vn -c:a aac <id>.m4a`).
   - Saved CDN URLs expire (403 after about 2 days). That's why the fresh URL is fetched and downloaded in one pass.
   - Recognize: `await Shazam().recognize(wav)` on three 12 s mono 16 kHz windows (start, 40%, end-12 s). Music under speech is still recognized most of the time. Two windows agreeing means a confident match.
   - Run the downloader, then the recognizer, as one background job with notify, because it's slow (about 3-5 s per reel).
4. **Aggregate.** For each track: number of uses, median outlier, max views and the dates. Rank by uses × outlier.
5. **Pick for the user's video.** Filter by mood fit with his clip, not popularity alone:
   - Instrumentals or instrumental sections beat vocal-heavy rap under speech. If the only hits have vocals, aim the stem at about -25 LUFS.
   - Mix 2-3 picks with talking-head-tiktok-edit's `mix_music.sh` (MAIN/ALT plus NO_MUSIC).
   - Log each track in the right brand library's CATALOG.md with the creator and video it came from.

## TikTok: free song IDs without Shazam
- A TikTok video page's `__UNIVERSAL_DATA_FOR_REHYDRATION__` → `webapp.video-detail.itemInfo.itemStruct.music.tt2dsp.tt_to_dsp_song_infos` often holds TikTok's own song match, even for "original sound" posts: `Platform 1` is an Apple Music trackId, `Platform 3` is a Spotify track id. In one run 91 of 164 posts had it.
- Resolve the ids in batch with `https://itunes.apple.com/lookup?id=<id1>,<id2>,...` (no auth, up to 100 ids) and `https://open.spotify.com/oembed?url=https://open.spotify.com/track/<id>` (title only).
- Use this first. Shazam is only needed for the rest. It's worth it because shazamio returns `RateLimited` for hours when several agents share the IP, and AudD's keyless quota is usually gone too.
- The profile-page `item_list` capture can return 0 items, so probe each video page instead (4 parallel Playwright workers do about 40 pages/min).
- To see the real status code, build `Shazam(http_client=HTTPClient(retry_options=ExponentialRetry(attempts=1)))`. With the default retry, a rate limit looks like a silent hang.

## Pitfalls
- **Local shazamio stuck on HTTP 429** (debug log shows `aiohttp_retry ... 429`; several agents share the IP): compute the signature locally — that part needs no network — then POST it from the cloud browser, which has a different IP. Steps: (1) locally run `sig = await Shazam().core_recognizer.recognize_path(value=wav)` and `payload = Converter.data_search(sig.timezone, sig.signature.uri, sig.signature.samples, sig.timestamp)` (from `shazamio.converter`), and dump all payloads to JSON. (2) In `browser_exec`, `goto_url('https://amp.shazam.com/discovery/v5/en-US/GB/web/-/track/40333609')` so the fetch is same-origin (from www.shazam.com CORS blocks it). (3) `fetch('/discovery/v5/en-US/GB/iphone/-/tag/<UUID>/<UUID>?sync=true&webv3=true&sampling=true&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3', {method:'POST', body: JSON.stringify(payload)})`, with an AbortController at 4 s, because `js()` times out at about 5 s. Gaps of 2.5 s plus a 12 s backoff on 429 identified 236 windows. A reference implementation is `~/IkkimiAssets/research/recent/romance/shz_sigs.py`.
- **Shazam skew tells you speed.** `matches[0].timeskew` / `frequencyskew` are positive when the clip is faster than the matched master (+0.05 for a 5 % speed-up; calibrated). When both are equal, it's a re-pitched speed change; when only timeskew moves, it's a tempo-only stretch. If no window matches, re-pitch the WAV (`asetrate=16000*r,aresample=16000` with r = 0.85…1.2) and retry. Sped-up or nightcore audio often only matches that way.
- The matched `offset` minus the window start gives the position in the track, i.e. which section the edit uses.
- Shazam rate-limits per IP: with several agents/processes recognising at once, `recognize()` hangs or times out (results look like "no match"). Wrap calls in `asyncio.wait_for(..., 30)`, run ONE sequential worker with 3-6 s gaps, record timeouts as errors (not misses) and retry them later.
- Anime/TikTok edits often use sped-up or slowed audio, which Shazam misses. If the normal window fails, retry the same window resampled: `-af aresample=44100,asetrate=44100*0.87,aresample=16000` (undo sped-up) and `*1.15` (undo slowed). This recovered several matches.
- The match `offset` minus the window start tells you which part of the song the edit uses.
- Whisper transcripts of these reels say nothing about the music. Use Shazam, not the transcript.
- A Shazam hit on just one window can be a sample or interpolation. Prefer tracks matched in 2+ windows, or used across several reels.
- **Local IP throttled (every `recognize` times out or returns empty, often because several agents share the IP)?** Split the work. Generate signatures locally with no network: `sig = await Shazam().core_recognizer.recognize_path(value=wav)` and `body = shazamio.converter.Converter.data_search(sig.timezone, sig.signature.uri, sig.signature.samples, sig.timestamp)`. Then POST each body from the cloud browser (`browser_exec`, a different IP): `new_tab('https://amp.shazam.com/')`, then `fetch` with POST to `https://amp.shazam.com/discovery/v5/en-US/US/iphone/-/tag/<UUID>/<UUID>?sync=true&webv3=true&sampling=true&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3`. It is same-origin, so CORS doesn't block it. Pace it at 3-4 s per call and back off 25 s or more on HTTP 429. This worked for 137 videos. A working helper is `~/IkkimiAssets/research/recent/hype_sigs.py` plus `hype_browser_shazam.py`.
- **Slowed/sped detection:** if a window gets no match, retry it resampled (`asetrate=44100*1.15` undoes a ~13% slowdown, `*0.87` undoes a speed-up). A match only at 1.15 means the edit used slowed audio. `matches[0].offset - window_start` gives where the edit's audio starts in the song (the section).
- In bash `while read` download loops, use `ffmpeg -nostdin` (and `yt-dlp ... < /dev/null`). Otherwise they eat stdin and truncate later lines, which corrupts the dir names.
- Charted hits (Kendrick, Kanye, Tyler) are copyrighted. They can't be baked into the user's file safely, so always deliver NO_MUSIC as well, so he can add the sound in-app.
