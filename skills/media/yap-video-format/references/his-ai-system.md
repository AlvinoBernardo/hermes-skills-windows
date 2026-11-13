# His AI system (in his own words) → what the user already has

Aiden says that every video from his sixth post on was edited by Claude Code. This file collects what he describes across 5 reels: DegOQG6Tydw, DeLhVyuT8G9, De0zboJzAlO, De55X5_TFTK and De8gyGETUWa. Full transcripts are in assets/aiden_reels_all.csv.

## Content pipeline ("how I edit reels with Claude Code", 300k views)
| # | His step | What he says | The user's equivalent here |
|---|---|---|---|
| 1 | Hook | "a document of 255 proven viral hooks. Claude picks the best one for my topic and compares them to my best performing videos" | `mino-lee-hooks` (229 proven hooks + formulas), plus the hook bank in this skill |
| 2 | Rough cut | "WhisperX timestamps every word… finds every breath, pause, filler word and cuts it. If I say a line twice, it chooses the better take" | `talking-head-tiktok-edit`: mlx-whisper word timestamps, RMS-dip cuts, keep the last clean take |
| 3 | Subtitles | "same transcript, two or three words on screen at a time" | caption styles A/B in talking-head-tiktok-edit |
| 4 | Music | "paste a link, it downloads with yt-dlp, files the song by feeling and vibe, suggests music based on topic. Half trending, half Plants vs. Zombies and anime soundtracks" | `~/PersonalBrandAssets/music/` + CATALOG.md, yt-dlp, mood matching |
| 5 | B-roll | "drop files in a folder and Claude labels and sorts everything… screenshots images off the web with an agent browser… a Mac mini runs an iPhone simulator that Claude taps through and records" | the asset library + CATALOG.md, headless-Chrome screenshots, `ios-simulator-marketing-capture` |
| 6 | Transitions | "hard cuts, a zoom every once in a while, making sure that things change every three seconds" | pop-up cards every ~3 s. **No punch-in zooms** (the user dislikes them) |
| 7 | CTA | "Comment real… nothing will happen because I'm too cheap for ManyChat" | the absurd-CTA joke slot in the templates |

He also has "rules distilled on how the hook is the only thing that matters, subtitles 2-3 words, something changing every 3 seconds". He edits "with FFmpeg and a bunch of custom Python scripts duct-taped together".

## Builder stack ("how I save 40 hours a week with AI", 5.7x)
- **Engineering:** T3 Code (Theo's agent control panel), with custom permission hooks, ~470 memory files, 28 skills and saved playbooks. "Scroll tech Twitter for an hour and steal all of it."
- **Design:** agents look through apps with good design, distill rules, then compare those rules against his app.
- **Testing:** a Mac mini as an agent sandbox (SSH over Tailscale, Xcode iPhone simulators). "84 end-to-end tests, 38 bugs in one night."
- **Code review:** Codex, "because I'm stingy".
- **Credibility receipt:** "~8 billion tokens in the last month"; "$200 a month to Anthropic".

## Agent principles (his two "101" videos, 12x and 10x)
1. Define the task and scope clearly, the same as for a human.
2. Give every sub-agent its own copy of the project (git worktrees).
3. "Baby-proof" the project: hooks block dangerous commands (no merge, no push to GitHub, no live-DB writes), so every mistake can be undone.
4. Have agents check other agents' work (design → build → test → review loops). "You'll wake up to bullcrap that has been reviewed by a couple other agents."
5. Make deliverables either clean outputs or decisions to make in the morning ("my morning report was 7 questions I answered in one line each").
6. "The bottleneck is authority, not the models." Front-load every decision and permission, then let it run with as many sub-agents as it needs. He gave the agent its own Mac mini with none of his passwords.

## His take on virality research (0.43x, but useful)
- An AI can predict retention reasonably well but not reach. In a Twitter study the content explained <5% of spread, and the messenger mattered far more.
- Same format, same editing: Hinge got 400k and Tinder got 6k.
- His superstition: the Trogdor shirt makes "a banger" even when the video is bad.
- **Lesson for the skill:** optimise what you control (hook, retention, receipts, jokes), post consistently, and never promise the user a view count.
