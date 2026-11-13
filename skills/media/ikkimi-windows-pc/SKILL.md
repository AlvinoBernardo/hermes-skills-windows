---
name: ikkimi-windows-pc
description: Use when running Ikkimi anime-edit skills on Windows.
---

# Ikkimi pipeline on the Windows PC

Load this alongside `ikkimi-anime-edits`, `anime-edit-engine`, `anime-footage-scene-index`, `short-form-video-critic-loop`, `social-viral-analyzer`. Those five are synced from the Mac and written in Mac terms; this skill is PC-only (not in the repo) so the sync never overwrites it.

## Paths
- Repo / assets root: `C:/Users/<you>/IkkimiAssets` (= the skills' `~/IkkimiAssets`; `~` resolves the same).
- Engine python: `C:/Users/<you>/IkkimiAssets/engine/.venv/Scripts/python.exe` (py3.12). Replaces `env -u PYTHONPATH ~/IkkimiAssets/engine/.venv/bin/python`.
- CLIP python: `C:/Users/<you>/IkkimiAssets/pipeline/.venv-clip/Scripts/python.exe` (CUDA torch, RTX 4070 Ti SUPER).
- Whisper models: `C:/Users/<you>/.hermes/cache/whisper/ggml-small{,.en}.bin`; `whisper-cli` is `C:/Users/<you>/tools/whisper/Release/whisper-cli.exe` (on the user PATH for new terminals).
- Hermes reads skills from `%LOCALAPPDATA%/hermes/skills/media`, NOT `~/.hermes/skills/media` (where the repo's setup/backup scripts copy them). `~/.hermes/skills/media` is a junction to the real folder so those scripts land in the right place.

## Rules
- **Never max out the user's PC: he works on it while jobs run.** On edit 14 the pipeline froze the PC ("I legit can't do anything on my computer"). It was running 12 parallel ffmpeg thumbnail decodes, a CLIP build, 5 pickers each loading SigLIP for every search, and a render, all at the same time. The rules:
  - Launch every heavy job (engine renders, index/thumbnail builds, CLIP builds, batch ffmpeg) through `C:/Users/<you>/IkkimiAssets/scripts/run_low.py`, run with the engine python. It sets below-normal priority and pins the job to half the logical CPUs, and the children inherit both. Use `--cpus N` to go lower.
  - Cap parallel ffmpeg pools at 4.
  - Run at most 3 pickers that use CLIP or vision at once.
  - Never overlap a render with an indexing job or a picker fan-out.
  - Tell the user before starting anything that will take more than ~5 min of heavy compute.
- **Never use `taskkill /IM python.exe`.** It kills every python on the box, including subagents' scripts. Kill one job with process_manage, or by PID.
- **When he says the PC is laggy, measure before acting.** Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/Users/<you>/IkkimiAssets/scripts/res_check.ps1` (python/ffmpeg priority, CPU-s and RAM, free RAM, CPU load) plus `nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv`. To lighten a running render without losing its progress, drop it to Idle: `Get-Process python,ffmpeg | ? PriorityClass -eq 'BelowNormal' | % { $_.PriorityClass='Idle' }`. Put that in a .ps1 file too.
- **Inline PowerShell from git-bash breaks on `$_` / `$var`**, because bash expands them inside double quotes. Write a .ps1 file and run it with `-File`.
- **CRLF from Windows Python:** text files it writes end lines in `\r\n`, so a bash `while read` loop puts `\r` into filenames and ffmpeg fails on every file. Do per-item ffmpeg loops in Python (a thread pool of 4 or fewer).
- **Show media can be missing on the PC (only `*.info.json` present).** Re-fetch it from the show's id lists with yt-dlp, one list per folder, for example `footage/blue-box/{nf_ids,tms_ids}.txt` plus a list built from `raw_scenepack/*.info.json` (`~/.local/bin/yt-dlp.exe -N 4 -f 'bv*[height<=1080]+ba/b' --merge-output-format mp4 -a <list>`). 48 clips took ~3 min. Then rebuild the CLIP inputs before any picker starts. The thumbs are a mid-frame grab per shot into each shot's `thumb` path (`edits/14-bb-her-template/work/make_thumbs.py`; cap its pool at 4). Then run `clip_index.py build <shots.json>` (~1 min on the GPU). Run both under `run_low.py`. Without them, pickers can't search and fall back to a curated 100-shot list, which gives duplicates and weak fits.
- The terminal tool is git-bash; native tools need `C:/...` forward-slash paths, not `/c/...`.
- Run the engine venv from `terminal`, not `execute_code` (PYTHONPATH clash, same as on the Mac).
- rembg uses CUDA here (`portable.onnx_providers()`), not CoreML. Ignore the skills' CoreML timings.
- Missing Apple fonts are auto-mapped by `engine/portable.py` (Hiragino -> Noto Sans/Serif JP, Helvetica -> Arial, Avenir Condensed -> Bahnschrift, Didot -> Bodoni Moda).
- Hermes's bundled ffmpeg is first on PATH and has no `drawtext`; label QA frames with PIL (as the engine skill says).
- `render_*.sh` scripts run in git-bash; swap the python path for the Scripts/python.exe one.
- Media (footage, music, mattes, CLIP embeddings) is not in git. Without the media tar from the Mac (`bash scripts/pack_media.sh essentials` there, then `tar -xf ikkimi-media-essentials.tar -C C:/Users/<you>/IkkimiAssets` + `engine/.venv/Scripts/python.exe scripts/remap_paths.py --apply`) only fresh edits with newly fetched footage can be rendered.
- **Backup push auth:** gh is logged in as AlvinoBernardo, but git didn't use it, and the push failed with "could not read Username". `gh auth setup-git` fixed it (done on the PC). The repo-local git identity is now set, and the first PC backup pushed: commit 374ade8.
- Sync with the Mac: `powershell.exe -ExecutionPolicy Bypass -File C:/Users/<you>/IkkimiAssets/scripts/backup.ps1` (restores Mac paths, commits, pulls, pushes, re-applies PC paths). Git always stores Mac-style paths. It needs a git identity: if the commit fails with "Author identity unknown", set it repo-local from the existing history (`git -C C:/Users/<you>/IkkimiAssets config user.name "Alvino Bernardo"` + `user.email you@example.com`, as in `git log`), then re-run. Run it with background=true: a failed commit leaves the pull-with-rebase stuck past the 180 s terminal default. A skill edit is live for new sessions as soon as it's saved locally; the backup only matters for the Mac.
- Format-skill mode was rebuilt (the Mac's `yap-video-format` / `mino-lee-hooks` scripts were never in git): `social-viral-analyzer/scripts/format/` = ig_reels_capture, ig_media_info, ig_owner_pass, tt_download_all, full_analyze, build_format_table, aggregate_format, CLASSIFY_INSTRUCTIONS.md. Verified on TikTok (@mkbhd: list 174, 6 downloads + full analysis in 30 s). The IG scripts are untested until the user does `ig_login.py`; on the first IG run, check the `/api/v1/clips/user/` paging and the scroll-capture fallback.
- `social-viral-analyzer` works on the PC (verified: TikTok fetch, prep, report, extract_hooks with RapidOCR + whisper, Shazam). Its SKILL.md has a "Prerequisites on Windows" section. The Instagram and TikTok-search logins (`ig_login.py` / `tt_login.py`) have to be done by the user in the visible window.
- PC edits to synced skills (social-viral-analyzer: `platforms`, Windows section, `scripts/ocr.py`, tool lookups + UTF-8 file I/O in extract_hooks/prep_media/build_report/music/*.py; they were wiped once by a Mac refresh and re-applied on 2026-11-10) only survive if they're pushed to the repo AND the Mac pulls before its next `backup.sh`; otherwise the Mac's `sync_skills.sh` (rm -rf + copy) reverts them. After any Mac->PC skill refresh, check that `scripts/ocr.py` still exists.
- GPU (RTX 4070 Ti SUPER, 16 GB) is verified for all three: rembg mattes (CUDA, ~0.2 s/matte), CLIP torch `2.11.0+cu128`, whisper-cli (CUDA0). A 4 s smoke render with mattes took 24 s.
- rembg CUDA needs `onnxruntime.preload_dlls()` before the session, or it silently runs on CPU ("CUDAExecutionProvider was requested but the session is running on CPU"). PC-local fix lives in `engine/portable.py onnx_providers()` (Windows-only branch); it's uncommitted until the user okays a push. If a `git pull` drops it, re-add it.
- `setup_windows.ps1` bugs: (1) `requirements-clip.txt` reinstalls CPU torch over the CUDA build. Fix: `uv pip install --python pipeline/.venv-clip/Scripts/python.exe --reinstall-package torch --reinstall-package torchvision torch torchvision --index-url https://download.pytorch.org/whl/cu128`. (2) the whisper asset is now `whisper-bin-win-cuda-12.4.0-x64.zip` (release b5454, not 'latest' v1.9.5, which has no assets). `gh release download b5454 -R ggml-org/whisper.cpp -p whisper-bin-win-cuda-12.4.0-x64.zip`.
- yt-dlp was missing on the PC (ref_dissect fails with WinError 2). It's installed via `uv tool install yt-dlp` into `~/.local/bin/yt-dlp.exe`; run `export PATH="$HOME/.local/bin:$PATH"` before ref_dissect.
- yt-dlp isn't on git-bash's PATH either (and not in either venv): `export PATH="/c/Users/<you>/AppData/Local/Microsoft/WinGet/Packages/yt-dlp.yt-dlp_Microsoft.Winget.Source_8wekyb3d8bbwe:/c/Users/<you>/tools/whisper/Release:$PATH"` before `ref_dissect.py` or downloads. shazamio lives in `C:/Users/<you>/.hermes/tools/social-scraper/.venv/Scripts/python.exe`.
- Engine renders on this PC: a 30 s landscape edit with ~70 rembg mattes took ~4 min cold, ~2 min warm. A 61 s edit with per-frame mattes under `run_low.py` takes ~6-7 min. Always start full renders with background=true + notify: a foreground terminal call that hits its timeout kills the render and leaves a half-written MP4.
- yt-dlp TikTok downloads sometimes fail with "Unable to extract universal data for rehydration". A plain retry a minute later worked, then pass the downloaded mp4 to ref_dissect.
- Shazam on the PC: `~/.hermes/tools/social-scraper/.venv/Scripts/python.exe` has shazamio (the engine and CLIP venvs don't). Run it sequentially with ~4 s gaps.
- uv isn't on git-bash's PATH: `/c/Users/<you>/AppData/Local/Microsoft/WinGet/Packages/astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe/uv.exe`.
- whisper-cli wants 16 kHz mono s16 WAV; a 44.1 kHz file exits silently after `read_audio_data`. Convert with `ffmpeg -ar 16000 -ac 1 -c:a pcm_s16le`.
- `git status` shows ~378 modified files after setup: that's `remap_paths.py --apply` (Mac paths -> PC) plus CRLF noise. Expected; `backup.ps1` restores Mac paths before committing. Never commit them by hand.
- Invoking the .ps1 from git-bash: pass a forward-slash path to `-File`; `scripts\\x.ps1` loses its backslashes.
