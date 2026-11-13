# Reused hooks: the phrases he used again and again, and how often they went viral

"Reused hook" = the same opening phrase used across several videos. The user wants THESE when he asks for "hooks that are proven" or "hooks he used multiple times that consistently went viral". Don't hand him a broad hook category, and don't hand him a single viral video.

Method (`scripts/hook_patterns.py`): run regexes over the spoken first line + on-screen text of all 1,139 talking videos. Count every use and how many of those went viral. Viral = at least 2x the median of the ~30 posts around it on the same account. Then judge the uses by hand: an IG + TikTok cross-post of the same video, or a repost of the same script, is NOT a separate use. Count different topics.

## Top 3: reused on 5+ different videos, best hit rate
| # | Format | Uses → viral | Different topics | Examples |
|---|---|---|---|---|
| 1 | "Is it possible to [X] in just [Y]?" | 26 → 16 (62%), median 2.83x | ~20 challenges, 2023-2026 | ace a midterm/final in 1 hour (6 uses, all viral: 60x, 39x, 28x, 63x, 4x…), arcade prize 52x, 3-min chest workout 28x, business in a day + $1k 24x / 20x, backflip in 1 hour 20x, $1k in 5 min with AI 3.7x. Misses: handstand 0.81x, tech startup day one 0.99x, app without code 1.16x, caffeine overdose 0.87x. He even posted "POV: you reused the same hook and got 24M views" (2.7x). |
| 2 | "I don't know who needs to hear this, but [belief] is not going to make you [goal]" | 10 → 7 (70%), median 5.19x | 8 | working harder won't change your life 20.6x, "average male thought pattern" stitch 19.9x, uninstalling video games 15.7x, storytelling sucks 8.1x, never a more convenient time (TT 3.8x / IG 1.06x), stitch 2.35x. Misses: "better to run a scam business" 1.13x, $62k course 0.92x. |
| 3 | "Here's (exactly) how I [X] so [result] every single time" | 9 → 5 (56%), median 3.30x | 6 | captions 93x (TT), script how-to 6.4x, hooks 8.7x (TT) / 0.55x (IG), script 3.3x. Misses: word hooks 1.1x, filming setup 1.2x. Strong on TikTok in 2023 (5 of 6), weak on IG (1 of 3). |

## Strong but only 1-2 different scripts (don't call them "reused formats")
- "At 21, I've briefly touched f*ck-you money": 4/4 viral, but 2 videos, each posted on IG + TT.
- "If you're Asian, you gotta start posting content, the competition could not be easier": 4/4, 2 videos.
- "The reason your account hasn't blown up is you care too much about views": 4/5, mostly the same script. The "I don't care if I get cancelled…" variant got TT 26.8x and IG 3.6x.
- "Here's how to get out of a slump": 4/6, viral 2022-2025. The 2026 reposts flopped (0.94x, 0.52x).
- "Apparently if you [weird hack], it makes you [extreme result]": 3/3 on IG, 0/1 on TT.
- "I can't afford [X]": 3/5 (the rent story and its follow-ups).
- "Here's the only video you'll ever need to watch to [X]": 3/5.
- Claude/AI-tool posts: 9/14 viral in Jul-Oct 2026, but they're a topic rather than a hook phrase, and they decay fast on IG.

## One-hit wonders and bad repeats (do NOT present as proven)
- "If you want to start creating content but you're afraid people will judge you… don't worry, they will": 1 of 5 uses went viral (2.6M once, then 1.42x, 0.71x, 0.44x). It's still OK as a one-off idea, but never call it a proven reusable hook.
- "If you want to [X]…" in general: 3/12. "[N] years ago I…": 2/16. "POV: …": 14/51 (27%).
- "Today is day [N] of road to $100k/month": 5/57. This is his worst repeated hook.
