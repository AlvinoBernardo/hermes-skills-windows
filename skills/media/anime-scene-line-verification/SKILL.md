---
name: anime-scene-line-verification
description: Use when verifying anime JP lines or JP-sub streams.
---

# Verify anime lines, timestamps and JP-subtitle availability

## On Windows (this PC)
Verified here: curl (git-bash `/mingw64/bin/curl`) fetches jimaku (4,631 entries parsed; Horimiya = `/entry/859`), `yt-dlp` 2026.10.26 (`~/.local/bin`, on PATH), JustWatch GraphQL returns data, `whisper-cli` is `C:/Users/<you>/tools/whisper/Release/whisper-cli.exe`.
- Set `PYTHONUTF8=1` for any Python that prints Japanese, or Windows pipes mangle it (cp1252). Parse the jimaku index in Python (`re` + `html.unescape` + `json`; some entries have null names, so stringify values before searching).
- JustWatch: send it from `curl -H "Content-Type: application/json" -A Mozilla/5.0 --data @query.json` (write the JSON to a file; git-bash quoting breaks inline). Python `requests` needs an explicit `User-Agent` header or it gets 403.
- `whisper-cli -l auto` needs a 16 kHz mono s16 wav (`ffmpeg -ar 16000 -ac 1 -c:a pcm_s16le`) and the multilingual model `-m C:/Users/<you>/.hermes/cache/whisper/ggml-small.bin` (not `.en`).
- Use `C:/...` paths for native tools. yt-dlp may warn about a JS runtime for YouTube; node is installed, add `--js-runtimes node`.

Never quote lines or timestamps from memory. Pull real subtitle files.

## 1. jimaku.cc (no login or API key needed for the web pages)
- `curl -sL -A Mozilla/5.0 https://jimaku.cc/` returns ALL entries (~4.6k) as `<div class="entry" data-extra="{json}"><a href="/entry/ID">`. html.unescape the JSON to get name, english_name, japanese_name and anilist_id. Grep it to find entry IDs.
- On the entry page `/entry/ID`, the hrefs `/entry/ID/download/<file>` are public, so curl them directly.
- File names show the source and therefore the timing. `.WEBRip.Netflix.ja[cc].srt` or `NF WEB-DL` = Netflix timing, and also proves Netflix carries a JP track somewhere. `[Timed to Crunchyroll]` = CR timing. BD/AT-X/TBS raws ≈ CR timing (±5 s). `Amazon.ja-jp[sdh]` = Prime.
- Parse srt and ass: in ass, keep only `Dialogue:` lines that contain kana/kanji and are under 90 chars. Typesetting ass files carry huge vector `m 123 l ...` lines, so filter those out.
- Gotcha: Re:Zero on Netflix is the 新編集版 (Director's Cut), so its timings differ from CR. The Oshi no Ko ep1 NF file is the 80–90 min single episode.

## 2. Streaming per country: JustWatch GraphQL (no key)
POST https://apis.justwatch.com/graphql with
`query S($f: TitleFilter!, $country: Country!, $language: Language!, $first: Int!) { popularTitles(country:$country, filter:$f, first:$first){ edges{ node{ objectType content(country:$country, language:$language){title originalReleaseYear} offers(country:$country, platform:WEB){monetizationType package{clearName}} }}}}`
variables `{"f":{"searchQuery":"Horimiya"},"country":"ID","language":"en","first":3}`. Some titles need their romaji name (Clannad shows up as 'Clannad').
- JustWatch can't tell you whether Netflix in a given region exposes the JA subtitle track. Mark that UNVERIFIED.

## 3. YouTube clip captions (no browser, so no stray autoplay tabs)
- `yt-dlp -J --skip-download URL`: `subtitles` holds HUMAN tracks; `automatic_captions` holds auto. Only `subtitles.ja` counts as human JA.
- Netflix Anime clips often have human ja tracks. Crunchyroll, Muse Asia, Aniplex and Netflix Japan clips usually have none or auto only.
- Check for burned-in subs on 1–2 ffmpeg frames: Netflix Anime clips are sometimes clean (logo only) and sometimes have burned EN subs.
- Netflix 'Multi-Audio Clip' titles switch dub languages line by line, so they're useless for a JP demo. Confirm with `whisper-cli -l auto` on a 12 s chunk.
- Search official channels: `yt-dlp --flat-playlist "https://www.youtube.com/@NetflixAnime/search?query=X"`.

## 4. Viral evidence
`web_search` snippets of TikTok URLs include views, likes, date and sound. Quote them with the URL. Know Your Meme pages work for meme lines.
