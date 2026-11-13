# aniclips.site: full-episode anime clips (user-recommended source)

`https://aniclips.site/anime?name=<slug>` has every episode cut into 10 s clips: clean 1080p HEVC at about 11-16 Mbps, 24 fps, with no subs or logos. The site is ad-heavy, so never browse it with a normal browser. Use the scripts, or a Playwright context that aborts third-party requests. This is unofficial footage the user chose (the rights risk is his call); log downloads in CATALOG.md as an aniclips source.

## Variants per clip
| variant | size | use |
|---|---|---|
| `hq` | about 15 MB, 1080p HEVC | final render only |
| `preview` | about 1.8 MB measured (FF average 1.76 MB; ep03 2.4 MB), 924x520 H.264, the full 10 s | indexing, picking, QA |
| `hover` | about 40 KB, 284x160, 5 s | rough scans |
| `thumbnail` | about 4 KB webp 284x160 | thumbnails |

## How it works (from the page JS)
- Clip lists: `https://cdn.jsdelivr.net/gh/adsjust460/aniclips-jsons@main/<slug>/meta.json` (gives `mal_id`) and `.../<slug>/ep<N>.json`, a list of `{id, start, end (ms), sources:{hq, preview, hover, thumbnail}}`.
- Key: `GET https://api.aniclips.site/api/episodes/<mal_id>/<ep>/key` returns `{key, iv_seed}` (hex). The fallback host is `https://bandagekey.aniclips.site`.
- Decryption: AES-CTR with the key, counter = HMAC-SHA256(iv_seed, clip_id)[:16], 128-bit counter length. All variants use the same scheme.
- jsDelivr returns 403 on large files. Rewrite to `https://raw.githubusercontent.com/<owner>/<repo>/main/<path>`, which works.

## Scripts
- Lean (default): `~/IkkimiAssets/pipeline/aniclips_lean.py`: `find <query>` (slug + mal_id + episode count), `index <slug> <out_root>` (preview-only download + shots.json + thumbs), `fetch-hq <slug> <ep> <t0> <t1> <out>` (HQ only for a time range), `index-local` (any folder of videos). Docs are in `~/IkkimiAssets/pipeline/README.md`.
- Catalog: the site's search box loads `raw.githubusercontent.com/malemsana2/aniclips-search/main/manifest.json`, which points to `search.<hash>.json.gz`. The `archive.json` at `cdn.jsdelivr.net/gh/adsjust460/bucket-bandage@main/archive.json` adds `mal_id`. Episode lists come from `meta.json` `episodes[]`; never probe `epN.json` in a loop (a single failed request used to drop episodes).
- Full HQ downloader: `~/IkkimiAssets/footage/fragrant-flower/aniclips/aniclips_dl.py <slug> <mal_id> <ep|all> <out_dir> [--start_ms A --end_ms B] [--workers 8]` (engine venv, needs `cryptography`). It's resumable.
- **List episodes explicitly and re-check counts after download.** A single failed meta lookup made an "all episodes" loop silently skip whole episodes. Some episodes on the site are genuinely partial (Fragrant Flower ep03 has only 35 clips).
- Fragrant Flower: slug `the_fragrant_flower_blooms_with_dignity`, mal_id 59845, 13 episodes.
- Dress-Up Darling: S1 `sono_bisque_doll_wa_koi_wo_suru` (mal 48736, 12 eps, 6,499 shots, ~15 min index), S2 `sono_bisque_doll_wa_koi_wo_suru_season_2` (mal 53065, 12 eps, 6,975 shots). `find kisekae` returns nothing; use `dress-up darling` / `sono bisque`. Both indexed with CLIP + op-ed on the PC (S1 ep12 ED is not flagged).
- **Some clips are missing on the site entirely** (S2 ep8 850-860 s: preview, hq, hover and thumbnail all 404). `aniclips_lean.py index` now tries hq when a preview 404s, then records a clip that 404s everywhere as a gap (`cache/epNN_missing.json`, `shots.json` `missing_clips_s`) instead of failing the whole episode. Before that fix one dead clip cost ~5 min of retries per attempt and failed the episode.
