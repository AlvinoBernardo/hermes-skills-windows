# Brain-model retention checkers (Meta TRIBE v2)

TRIBE v2 (`facebook/tribev2`) predicts fMRI responses to video, audio and text. Hub skills wrap it to score a video's hook, retention and emotion using Yeo-7 brain networks: VAN for surprise, DMN for boredom, DAN for tracking, Limbic for emotion.

## Hub candidates
| Hub id | What it is | Verdict |
|---|---|---|
| `skills-sh/varnan-tech/opendirectory/meta-tribe-skill` (repo dir `skills/meta-tribeV2-skill`) | FastAPI/RunPod server plus a report prompt | Do not install as-is |
| `skills-sh/hiyenwong/ai_collection/tribe-v2-multimodal-brain-foundation` | A paper summary, not a tool | Not useful for video checks |

## Why meta-tribe-skill was rejected
The skills.sh audit results were 2 warnings and 1 pass. Code review found the following:
- **Data leak:** `download_and_analyze.py`, `wait_health.py` and `deploy_to_persistent.sh` hardcode the author's AWS IP. Run unchanged, they send the user's video links to a third party.
- **Cost and exposure:** `launch_persistent.sh` starts a persistent g5.12xlarge (about $5–6 an hour) with ports 22 and 8000 open to 0.0.0.0/0, and the API has no auth.
- **Shell injection:** yt-dlp saves files as `%(title)s`, and ffmpeg runs through `shell=True` with that path. A crafted video title can execute commands.
- **Fake speech input:** `server.py` monkeypatches transcription to a fixed sentence, so the language and speech part of every score is meaningless. `runpod_handler.py` does not do this.
- **Weak benchmarks:** the view predictions rest on about 5 of the author's tech/AI videos.
- **License:** the model is CC BY-NC 4.0. Using it to optimise marketing for a paid app is arguably commercial use.

## If the user still wants it
This is for testing only, because of the NC license. Use `runpod_handler.py`-style real transcription, remove every hardcoded IP, call ffmpeg via an argv list (no `shell=True`), use a GPU that shuts itself off, and keep the per-second engagement curve from `scripts/local_analyze.py` (valleys below z −1 for at least 4 s are cut candidates). Present the output as a model prediction alongside the critic loop, never as real retention data.
