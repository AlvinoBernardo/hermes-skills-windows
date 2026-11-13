# What flops (and the stats behind the rules)

108 reels older than 7 days. Outlier is views divided by the median of the 30 surrounding posts. A hit is 2x or more; a flop is under 0.7x.

## By hook type
| hook_type | n | median | hit % | flop % |
|---|---|---|---|---|
| famous_person_breakdown | 3 | 10.37 | 67 | 0 |
| bold_claim_reveal | 7 | 1.48 | 29 | 29 |
| here's_how_explainer | 6 | 1.38 | 17 | 17 |
| controversial_stat | 5 | 1.23 | 40 | 0 |
| quote_or_philosophy | 6 | 1.20 | 33 | 33 |
| here's_my_system | 6 | 1.14 | 33 | 17 |
| personal_stakes_story | 11 | 1.10 | 18 | 18 |
| relatable_confession | 13 | 1.07 | 8 | 8 |
| announcement_or_contest | 5 | 0.88 | 0 | 0 |
| **daily_update** | **35** | **0.81** | **0** | **37** |
| question_hook | 6 | 0.72 | 17 | 50 |

## By topic
| topic | n | median | hit % |
|---|---|---|---|
| race/culture stats bait | 4 | 12.84 | 50 |
| college/career/CS/quant | 7 | 2.70 | 57 |
| tech news & famous people | 3 | 1.56 | 33 |
| AI tools & workflow | 10 | 1.17 | 20 |
| self-improvement philosophy | 10 | 1.06 | 10 |
| school-life vlog | 13 | 0.94 | 0 |
| hackathons & builds | 6 | 0.94 | 33 |
| dating apps | 9 | 0.89 | 33 |
| **founder journey (his own app)** | **45** | **0.84** | **7** |

## By structure
| structure | n | median | hit % | flop % |
|---|---|---|---|---|
| tutorial / system walkthrough | 4 | 1.73 | 50 | 0 |
| stat → twist joke | 9 | 1.38 | 33 | 11 |
| chronological story | 17 | 1.21 | 24 | 12 |
| explainer breakdown | 7 | 1.08 | 29 | 43 |
| hot take argument | 11 | 0.95 | 18 | 9 |
| numbered list | 5 | 0.82 | 40 | 40 |
| **vlog update** | **40** | **0.82** | **2** | **40** |

A numbered list is high-variance: the Hinge and Claude Code lists hit big, and the Tinder list and the self-help lists flopped.

## Other signals
- **Text hook on screen:** 1.10x / 22% hits with one, 0.96x / 9% without.
- **Length:** under 30 s 0.94x (6% hits) · 30-60 s 0.91x (11%) · 60-90 s 1.37x (33%) · 90 s+ 1.61x (44%).
- **Opening with "day N":** 23 reels, 0.87x, 0 hits.
- **Hook devices** (median, hit %):
  - chart/visual reference 2.24x (57%)
  - curiosity gap 1.30x (41%)
  - controversy bait 1.23x (37%, 0% flops)
  - self-deprecation in the hook 0.90x (9%)
  - question 0.99x (7%)
- **Voice devices** (median, hit %):
  - absurd CTA joke 2.08x (56%)
  - insider jargon explained 1.31x (32%)
  - self-deprecating jokes overall 0.91x: fine inside the video, bad as the main act
- **Visual devices** (median, hit %):
  - numbered section labels 3.41x (n=6)
  - web-page b-roll 1.29x
  - meme pop-ups 1.23x
  - app screen recordings 0.82x (they come with product posts)
  - face cam only 0.81x
- **Speed and cuts are NOT the difference.** Hits and flops both ran at ~240 wpm. Hits averaged 1.55 cuts/10 s against 1.84 for flops.

## Patterns that reliably flop
1. **Diary openers:** "Alright, day 36…", "Didn't do anything today", bug counts, App Store paperwork. They hold nothing for a stranger.
2. **Product pitch as the topic:** "What's different about my dating app?" (0.62x), feature updates, launch trailers.
3. **Local asks:** UT-only contests and hiring posts (0.71-0.88x).
4. **Borrowed business frameworks with no personal stake:** Hormozi's value equation (0.41x, his worst), NPS (0.58x), "Focus is subtraction" (0.47x).
5. **Remakes of a hit with a weaker brand or angle:** the Tinder reverse-engineering remake (0.54x vs Hinge's 37x), and a hackathon sequel with a confusing title (0.64x).
6. **A hook that promises value the video doesn't pay:** "$4K of AI credits, 3 lessons" that became "I didn't learn anything" plus a birthday vlog (1.1x), and a "POV: AI spend approaching 5 figures" title on a progress update (0.55x).
7. **Leaving the format:** a slow street interview at 190 wpm with the twist saved for the end (0.57x).
8. **Meta "can AI predict virality" research** (0.43x). Interesting to creators, irrelevant to everyone else.
