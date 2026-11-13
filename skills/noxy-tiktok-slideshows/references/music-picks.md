# Music picks per slideshow

When the user asks for viral music for slideshows: sounds are added IN APP, so deliver per-package picks (primary + backup) with sound links, not audio files.

1. Evidence first: pull the `music` struct (title, authorName, id, original) of top posts in the SAME format from saved reference manifests / scout URLs via the rehydration JSON (`webapp.video-detail` itemStruct.music, same fetch as `scripts/tt_post_fetch.py`). Fetch sequentially with ~1.5s gaps; parallel requests get rate limited (no rehydration data).
2. Usage counts: open `https://www.tiktok.com/music/x-<id>` in the browser and read innerText (`145.5K videos`). The SSR HTML has no music-detail data.
3. Live chart: octohog.com/tools/trending-tiktok-sounds (refreshed twice daily, shows brand clearance) or trendingtiktoksongs.com (US weekly, risers, new entries).
4. Prefer sounds proven on same-format posts with a moderate video count. Use the chart as backup or for soft aesthetic girl posts.
5. Flag that a Business account only gets the Commercial Music Library, so user-uploaded original sounds may be unavailable. Give a licensed backup.
6. Never promise a sound makes a post viral.

## Workflow that worked (batch61)
- Run `scripts/tt_music_fetch.py` on the post URLs. It is sequential, caches results and handles about 100 posts in 4 min. Group the results by music id: a sound used on 2 or more same-topic winners is the strongest pick.
- Find same-topic winners in the browser on `tiktok.com/search/photo?q=<query>`. The first line of each card is likes, the last line is the date (`6-15` = this year). Scroll once to get 12 cards. Keep 2026 posts with 20K+ likes, then fetch their music.
- Check for speech or lyrics before picking a sound for @noxy.app. Download `music.playUrl` (use a Referer of tiktok.com), convert it with `ffmpeg -ar 16000 -ac 1`, then run `whisper-cli -m ~/.cache/openwhispr/whisper-models/ggml-large-v3-turbo.bin -l auto -nt`. Output like `*music*`, or junk such as `Субтитры сделал…` or `We'll be right back.`, means beat only. Batch 60's 'Original invincible sound' has a spoken 'I'm invincible' line, and Brivex Originalton has 'I kissed a girl' lyrics.
- Use the music struct flags to judge business-account risk. Label tracks have `isCopyrighted=true` and `is_commerce_music=false`, so treat them as personal-account only (Kingdom Beat/Valterix is one of these, so it is NOT a business-safe pick). User beats with `isCopyrighted=false` and `is_commerce_music=true` may work. Still tell the user to confirm the in-app 'Commercial use' label.
- For business fallbacks, use the Octohog 'Cleared' column. Prefer a cleared official track by the same artist as a fan-upload primary (for example 'nothing' by Steve Lacy).
- Batch61 picks: `Finished-slides/emily-manga-61/MUSIC.json` and `fox-manga-61/MUSIC.json`, plus `emma-61/MUSIC.json`.
- In photo search scrapes, drop links containing the logged-in account's numeric id (notification panel cards such as 'X liked your photos') before parsing likes. Opening single post pages in the browser can trigger a slider captcha. Close it and use `tt_post_fetch.py` (urllib) to view slides instead. Never solve the captcha.
- Format signature sounds: the 'girlies, don't go to the gym until you KNOW these things' hook runs on 'original sound - rockstardannyvarr' (7493351586549386030, a moody folk song clip, about 970K videos) on 8 top posts. Its runner up is PinkPantheress 'Illegal' (3 @allyfitn posts). Aesthetic weight loss tips slideshows have no shared sound, so pick a soft, warm 2026 single winner (Cleo Sol 'Life Will Be', @lilcolette_ 886K).

Batch60 picks: `Finished-slides/four-female-two-male-60/MUSIC.json` (CKay love nwantinti for food swaps, wonniech sound for weight-loss tips, girl in red october for diary, liliesleah Try for girl gym tips, Original invincible sound / Brivex Originalton for fox manga).
