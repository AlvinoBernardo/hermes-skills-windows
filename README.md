# Hermes Skills — Windows pack

26 custom Hermes Agent skills, ready for a Windows PC.

## Install (Windows)

1. Install [Hermes Agent](https://hermes-agent.nousresearch.com/docs) and run it once.
2. Open **PowerShell** and run:

```powershell
git clone https://github.com/AlvinoBernardo/hermes-skills-windows
cd hermes-skills-windows
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

No git? Click **Code → Download ZIP**, unzip, then run the `install.ps1` line from inside the folder.

Skills are copied to `%LOCALAPPDATA%\hermes\skills`. Any skill you already have with the same name is moved to `%LOCALAPPDATA%\hermes\skills-replaced-<timestamp>` first (nothing is deleted). Restart Hermes afterwards.

Options: `-DryRun` (preview only), `-Only name1,name2` (install just some).

## Notes

- Paths like `C:/Users/<you>/...` and `~/Desktop/...` were written for the original owner's machine — Hermes will adapt them, or edit them to your own folders.
- Some media skills expect tools (ffmpeg, yt-dlp, Python venvs) that you'll need to install; the skill text says which.
- The `noxy-*` and `ikkimi-*` skills are tied to specific projects — use them as templates.

## Skills

| Skill | Category | What it does |
|---|---|---|
| `opencode` | autonomous-ai-agents | Delegate coding to OpenCode CLI (features, PR review). |
| `codex-image-generation` | — | Use when generating images through Hermes Codex auth. |
| `design-md` | creative | Author/validate/export Google's DESIGN.md token spec files. |
| `anime-edit-engine` | media | Use when rendering a TikTok anime edit from a spec. |
| `anime-edit-thinking` | media | Use when planning an anime edit: refs to story to beats. |
| `anime-footage-scene-index` | media | Use when sourcing anime footage + building a scene index. |
| `anime-scene-line-verification` | media | Use when verifying anime JP lines or JP-sub streams. |
| `gif-search` | media | Search/download GIFs from Tenor via curl + jq. |
| `ikkimi-anime-edits` | media | Use when making Ikkimi anime edits or edit-to-app CTA videos. |
| `ikkimi-face-account-scripts` | media | Use when writing Ikkimi face-account anime scripts. |
| `ikkimi-windows-pc` | media | Use when running Ikkimi anime-edit skills on Windows. |
| `mino-lee-hooks` | media | Use when the user needs a hook for a video or slideshow. |
| `short-form-video-critic-loop` | media | Use when critiquing a Reel draft for retention or voice. |
| `social-viral-analyzer` | media | Use when analyzing a creator's viral posts, hooks or format. |
| `songsee` | media | Audio spectrograms/features (mel, chroma, MFCC) via CLI. |
| `talking-head-tiktok-edit` | media | Use when scripting or editing talking-head TikTok clips. |
| `yap-video-format` | media | Use when scripting talking-head yap or 48 Laws videos. |
| `noxy-ai-fitness-videos` | — | Use when creating Noxy AI fox fitness-explainer videos. |
| `noxy-hook-demo` | — | Use when making Noxy UGC hook-to-demo videos. |
| `noxy-tiktok-slideshows` | — | Use when making Noxy TikTok slideshows. |
| `box` | productivity | Box manages cloud files, sharing, search, and metadata. |
| `macos-disk-cleanup` | productivity | Use when the Mac or Windows PC is low on storage. Audit, explain, delete. |
| `macos-printing` | productivity | Use when finding, setting up, or printing to a Mac or Windows printer. |
| `llm-wiki` | research | Karpathy's LLM Wiki: build/query interlinked markdown KB. |
| `mcp-server-development` | software-development | Use when vetting, building, or hardening MCP servers. |
| `python-debugpy` | software-development | Debug Python: pdb REPL + debugpy remote (DAP). |
