---
name: anime-footage-scene-index
description: Use when sourcing anime footage + building a scene index.
---

# Anime footage sourcing + scene index

Get official PVs, OP/ED and clips, scene-detect them, make contact sheets, annotate every shot.

## Sourcing
- Find official uploads with `yt-dlp --flat-playlist --print "%(id)s | %(duration)s | %(channel)s | %(title)s" "ytsearch20:<q>"`, then list channel searches directly: `https://www.youtube.com/@aniplex/search?query=<JP title>`, `@MuseAsia/search?query=...`, `@Crunchyroll/search?query=...`. Search the JP title + ノンクレジット / ノンテロップ for creditless OP/ED (Aniplex uses ノンテロップ for older shows).
- Many Crunchyroll S1-era clips in playlists return "Video unavailable" (region/removed) — probe with `yt-dlp --print` before planning around them.
- Download: `yt-dlp -f 'bv*[height<=1080]+ba/b' --merge-output-format mp4 --write-info-json`. Build sources.json from the info.json files.
- Text reality: Aniplex PVs = JP captions/name cards on many shots; Muse Asia = burned EN subs + logo; Crunchyroll clips = CR watermark top-left + end screen (usually no burned subs); Crunchyroll trailers = burned subs. Creditless OP/ED are the cleanest. Aniplex/Muse #shorts are native 608x1080 vertical.

## animeclips.online (WP use-your-drive plugin, Google Drive folders)
- Show page has Season tabs = Drive folders, each with per-episode subfolders of per-SHOT MP4s (2-20 s, 1920x1080 24fps H.264 ~18 Mbps, AAC; contiguous within an episode, OP/ED excluded). Dress-Up Darling S2 = ENGLISH dub (~2830 clips, 20 GB); S1 = Japanese.
- List: POST `/wp-admin/admin-ajax.php` `action=useyourdrive-get-filelist&id=<folder>&listtoken=<data-token>&account_id=<data-account-id>&lastFolder=<parent>&folderPath=<b64 json [root,season,folder]>&_ajax_nonce=<from page XHR>&sort=name:asc` (capture one real call by hooking XHR and clicking the tab). Response JSON `html` holds every file (`<div class='entry file' data-id=...>`, name, duration, size) in one go.
- Download: GET `admin-ajax.php?action=useyourdrive-stream&account_id=..&id=<fileid>&listtoken=..` (or `useyourdrive-download&dl=1`). Direct `drive.usercontent.google.com` needs sign-in (fails). The WP.com CDN sometimes caches an EMPTY text/html reply: alternate the two actions + add `&cb=<n>` on retry. Site WAF 403s the whole IP after ~13 GB in ~35 min at 11 parallel; 3 workers (~5 MB/s) ran 8 GB clean. Script: `edits/09-dud-dub-edit/dub/tools/dl.py`; then prep_audio.py (sample-exact concat per ep) + transcribe.py (whisper small.en `-nfa -mc 0 -dtw small.en -ojf`; `-mc 0` is needed or it loops on music; DTW is off under flash-attn) map words back to clips.
- Grep the transcripts first, then keep only episodes with the lines (DUD S2 romance: E10 confession monologue, E06 pageant 'dazzling', E12 'I love you, Gojo'/selfie/plush rehearsal).

## Scene detection
- `ffmpeg -i f -vf "select='gt(scene,0.3)',showinfo" -an -f null -` → pts_time; merge cuts <0.4s. ~40 s per 90 s source.
- Then re-split shots >8s with threshold 0.12 (catches dissolves in EDs/dialogue clips). Reference scripts: ~/IkkimiAssets/footage/dress-up-darling/tools/detect.py and refine.py (thumbs at mid-shot 320px, 6x5 sheets with id+duration printed via PIL).

- Slideshow/picture-in-frame videos (e.g. Aniplex "special movie") defeat scene-score even at 0.05: diff tiny gray frames (fps=4, scale 48x27) 1 s apart and cut at local peaks >18. Use output seeking (`-i f -ss a -t d`); input seeking + select returned 0 frames on a VP9 file. Script: ~/IkkimiAssets/footage/fragrant-flower/build_shots.py.
- Netflix Anime vs Netflix Japan often upload identical clips: Netflix Anime = burned EN subs + NETFLIX logo; Netflix Japan = clean (logo only in outro). Netflix JP "recap" videos have burned JP subs.
- Aniplex NCOP/NCED (2025+) keep song credit bottom-left + series logo bottom-right; artist "anime ver." MVs have small vertical lyrics at the right edge. Both are clean after a 9:16 center crop, so flag `crop916_clean` separately from `clean`.

- Black Clover findings (ref scripts ~/IkkimiAssets/footage/black-clover/tools/):
  - TV Tokyo (テレ東アニメ) has creditless S2 OP/ED, 振り返りPV recaps and a 10-min clean S1 recap. Its episode-insert clips carry a top-right logo bug.
  - Crunchyroll 'Opening N' uploads are NOT creditless (staff credits) and are letterboxed.
  - Older CR clips are 720p with burned EN subs. Search JP titles (ノンクレジット, PV, 予告) first.
- Fresh-episode BC footage (S2 ep3+): neither animeclips.online nor aniclips.site carries Black Clover. YouTube per-character twixtor/scene packs uploaded within days of airing (Cat Anime, Wyunye, DETOS, RingWitDaHoodie, Zens.Twixtor2.0) cover nearly every shot. Search `black clover season 2 episode N twixtor` + `<character> twixtor`, fetch about 16 packs with `xargs -P 5` yt-dlp (about 30 s), then `index-local` + `clip_index.py build` (about 80 s). That found 20 of 25 ref shots exactly for edit 13 (`footage/lean/bc_s2_ep3`). Pack caveats: DETOS ep mixes (Uk02A96P2nA) carry a centre 'TWIXTOR CLIPS IN DESCRIPTION' watermark, and inpainting it leaves visible garbage, so swap those shots. wBQQ8euFp3Y has a faint watermark at y ~0.87 (fix: zoom 1.2 top-anchored). ONE J BRO 4K uploads (OSnV3gJgrmQ) have burned EN subs at y>0.80 (fix: zoom 1.26 top-anchored).
- Letterboxed OP/ED/PVs: confirm with `cropdetect=24:2:0` and record the crop string in notes.
- The scene-detect over ~50 min of 1080p takes ~12 min. Run it in the background and poll; a foreground sleep over 400 s times out.

## aniclips.site episode clips (10 s contiguous files)
- Scripts: ~/IkkimiAssets/footage/fragrant-flower/aniclips/index/tools/process_ep.py (one ffmpeg pass per clip: scene-detect at 480px + fps=6 frames, 6 workers, ~90 s per 144-clip episode) and merge.py (pipe annotations with `@ setting ; mood` defaults and `SEC.k-SEC.k` ranges -> epNN.json, asserts full coverage).
- To get a priority episode sooner, run a second `aniclips_dl.py <slug> <mal> <ep>` alongside the main loop. It skips existing files, and one episode arrives in ~3 min.
- Clips are contiguous, so concatenating their audio gives exact episode time. For JP dialogue use the multilingual `~/.hermes/cache/whisper/ggml-small.bin` with `-l ja` (24 min in ~2.5 min). Its segment times are 1-2 s coarse; refine with 0.5 s RMS windows. Spectral flatness tells the bed apart: ~0.55-0.8 means ambience/waves, ~0.2-0.4 means tonal music, and -180 dB means deliberate dead air.

- Blue Box findings: TMS (@TMSanimeJP) has every creditless OP/ED (S1 cour 1+2, S2), the PVs and 15 s 次回予告 previews. The previews carry a 次回予告 tag top-left at [120,62,262,98]. Netflix Japan Chinatsu clips (16:9) are clean and give lip-syncable JP dialogue, but their 第N話ラストシーン clips are 608x1080 crops. TMS アオのショートバコ shorts are vertical with JP+EN subs, so use them for audio only. Netflix JP trailers DO carry burned JP subs on some shots.
- Character IDs: anime Chinatsu = light-brown hair; Hina = pink. Confirm a character's look from an official character-PV name card before trusting a brief.
- Fan twixtor/scenepack uploads can hide a faint full-length watermark that a 260 px sheet misses. Run a persistent-edge detector first: Canny over about 48 frames, keep pixels with an edge in more than 50 % of frames (ref ~/.hermes/cache/scratch/bb/static.py). It caught "DOWNLOAD THE TWIXTOR…" on Li1C50oWSvQ. cv2 seeking is slow, so run it in the background.
- Dialogue lip-sync check: the ffmpeg fps-filter tile sheets start offset from -ss, so confirm speaker and shot bounds with single frames at exact times plus `select=gt(scene,0.15)` cuts.

## Verifying JP lines, timestamps and where to stream (Ikkimi demo scouting)
- jimaku.cc homepage HTML (~2.5 MB) lists every entry as `<div class="entry" data-extra="{json}"><a href="/entry/N">`. Parse it once to map show -> entry. Each entry page lists `/entry/N/download/<file>` links. Html-unescape and re-quote the href before downloading, or names with `&` or `#` return 404. Grep the episode .srt/.ass for the quote to get exact JP text and mm:ss. No API key is needed. Netflix `ja[cc]` and Amazon `ja-jp[sdh]` rips in an entry also prove that the platform carries a JP track somewhere.
- Netflix per-country language lists: `curl -sL -A '<Chrome 130 UA>' -o f.html https://www.netflix.com/id-en/title/<id>`, then regex `|Audio|...|` and `|Subtitles|...|` from the tag-stripped text. urllib's default UA gets redirected to /unsupportedbrowser. The lists are title-level, and the season list in the HTML stops after 10 seasons.
- YouTube official clips (TOHO, Aniplex, Crunchyroll) almost never have human JA captions. Use `yt-dlp --list-subs`: `ja-orig` there is only ASR and it garbles anime lines.
- TikTok popularity per character: ninjaclips.io/characters/<first-last> gives score, edit views, 7-day gain and trending rank. Guess the slug as full name (kyojuro-rengoku, sung-jinwoo). A wrong slug silently returns the index page.
- Jisho API `jisho.org/api/v1/search/words?keyword=` gives JLPT tags for click-word picks.

## Annotation
- vision_analyze downscales anything wider than ~1000 px by 2x, and region crops get the same treatment. Row-per-clip sheets (12 clips x up to 8 thumbs at 240 px) come out at ~117 px per tile: fine for coarse labels, but not for reading small text.
- vision_analyze loads the sheet into your own context — you write the annotations yourself. Use a compact pipe format per sheet file (id|desc|chars|shot|energy|mood|iconic|fanservice|text codes, with id ranges like `S01-045..053` for repeated loops), then expand in Python and assert every shot id is covered exactly once.
- clean = no text codes at all. Re-check money-shot candidates on a 640px sheet — small song credits/captions are invisible at 320px.
- vision_analyze halves big sheets unpredictably (1300x1176 sometimes kept, sometimes halved; 1560+ wide always halved). Reliable: tiles of 260px in 1300x672 images (5x4). Crop 5x7 sheets into top/bottom halves before viewing. Script: aniclips/index/_work_ep01-04/{shots,sheets,build}.py (pipe-format annot with id ranges -> JSON, asserts full coverage).
- Fragrant Flower friends (per kaoruhana.fandom wiki, NOT the 'Saku = glasses' brief): Saku Natsusawa = tall, long black bangs to the nose, gray cardigan, gloomy; Ayato Yorita = shorter, short black hair with ahoge, cheerful; Shohei Usami = red-orange spiky hair, yellow hoodie. The glasses guy in a tie who tutors them in ep3 and hands out tests in ep4 is someone else (teacher/classmate?). Subaru Hoshina = silver/mint long ponytail, green-aqua eyes (first appears ep4). Rintaro's mother = blonde ponytail, chef whites. aniclips.site ep3 only has 35 clips (0-350 s).
- aniclips 10 s episode clips (Fragrant Flower): tools at footage/fragrant-flower/aniclips/index/tools/. Run shots_sheets.py N --stage overview first: it makes one 12x12 frame-per-clip sheet that finds the OP/ED quickly. The OP title card comes about 11 s after the OP starts, and the ED starts at about 1350 s. Then run --stage sheets --skip <OP clips>,<ED clips>, write the compact annot txt, and run build_ep_index.py N, which asserts full coverage. Shots that cross a 10 s clip boundary get split into two entries, so when you pick money shots, take the longer half.
- The aniclips_dl.py 'all' mode probes each epN.json only once, so it silently skipped ep6/ep7. Check the dl.log lines against the episodes/ dirs and re-run missing episodes one at a time.
- vision_analyze often halves sheets (1500 px down to 750 px). 5x6 tiles at 300 px are still readable for content, but recheck character IDs on full-res frames.
- More Fragrant Flower IDs: the long-blond-PONYTAIL chef in a cap at Plain is Rintaro's MOM, not Rintaro. Ayato = the short-black-haired friend with no glasses. The man with glasses in a green track jacket is a teacher. Subaru = mint/white hair, usually in a ponytail. The thugs in ep7 = a blond guy in a purple tee plus friends in a hoodie and a cap.
- Fragrant Flower character check: Rintaro is BLOND (spiky, ring earrings). Under the blue alley light in the Netflix clip he reads as silver-haired in a teal hoodie. Black-haired boys are Saku/Natsusawa, and the orange-haired guy with earrings is the alley thug. FF0602 (Kaoruko) and FF0312 (likely the thug) were labelled 'Rintaro'. Check any 'Rintaro' shot for blond hair before you use it.
