# Scouting viral TikTok slideshow formats for approval

Use this when the user asks to find formats like an existing winner (for example "more formats like Eat This Not That") that went viral recently, and wants to approve them before production. This is the one case where presenting options for approval IS the deliverable. The no-approval-gates rule applies to production batches, not to scouting.

## Procedure
1. **Know the reference first.** View the winning format's preview (for example `viral-recreations-20261008/v4-food-swaps/preview.jpg`) so you know what "like that" means: the comparison mechanic, how much text, and the visual style. Note the target account's rules (Emily allows illustrated AI; Emma allows real photos only).
2. **Search TikTok's Photo tab in the browser** (`https://www.tiktok.com/search/photo?q=<query>`). Results show likes and dates without login walls. Run 50+ queries covering the mechanic and its neighbours: swaps, "eat this not that", calorie comparison, "what 100 calories looks like", guess the calories, higher vs lower calorie, grocery/snack/drink/takeaway/coffee-order swaps, cheat sheets, infographics. Batch about 12 queries per call and persist results to a workspace JSON after each query.
   - Infinite scroll: scroll the LAST result anchor into view plus `window.scrollBy(0,2000)` and repeat until the body text ends with `No more results` (about 30 to 50 results per query). Scrolling only `document.body` stalls at about 12.
   - Filter out notification cards ("liked your", "started following", "replied to"): the logged-in session's notification popups also contain `/photo/` links.
   - Never like, follow or comment from the session; it may be the user's account.
3. **Date every post from its ID**: `created = post_id >> 32` (unix seconds). Treat "recent" as about the last 90 days, and shortlist posts with 3K+ likes.
4. **Fetch real views and every slide server-side** with `scripts/tt_post_fetch.py <hrefs.json>`. It requests the `/video/<id>` URL (a `/photo/` URL returns no detail data) and parses `__UNIVERSAL_DATA_FOR_REHYDRATION__` → `webapp.video-detail.itemInfo.itemStruct`. That gives `stats.playCount`, `createTime`, `desc`, `imagePost.title` and `imagePost.images[].imageURL.urlList[0]`. Opening posts in the browser triggers a slider captcha, so do not. Some fetches return no data from rate limiting; wait about 20s and rerun (the script caches finished posts). `yt-dlp -j <video url>` also returns `view_count` as a cross-check.
5. **Look at every candidate.** Build contact sheets (one row per post: handle, views, date, slide count, up to 8 slides) and view them yourself. Drop off-topic hits (zodiac, movies, generic recipes), and group posts into distinct FORMATS, not individual posts.
6. **Rank formats by repeatable evidence.** Several accounts, or a numbered part series, beats a single viral post. Note when a format comes from a calorie-app brand (for example Fitatu) or puts an app CTA mid-deck (a SwapIt-style app slide), because that maps directly onto Noxy. Say plainly when a format has only one proving post.
7. **Deliver for approval.**
   - Inline widget (`_preview.html` with base64 thumbnails): one card per format with a slide strip, view counts with dates and links, why it works, and how it would look for the target account (for Emily: cream/terracotta, the ponytail girl, a real Noxy slide, generic foods instead of brand packaging). Add `data-hermes-send="Approve format N (...) for Emily"` buttons plus an Approve-all button.
   - Also a summary table in the reply, a master `_preview.jpg` via MEDIA, and the folder `Desktop/Noxy/Noxy-<date>-<Account>-Format-Scout/` with numbered format folders (reference slides, `_preview.jpg`, `NOTES.txt` with links and stats), `FORMATS.md`, and a tested ZIP. Open it in Finder.
   - Pillow's Arial cannot draw emoji (they render as boxes). Swap emoji for words in JPG labels and keep emoji only in the HTML.
8. State that view counts are public post data from the scout date and do not promise results for the user's account. Do not produce slideshows until the user approves formats.

## Helper pitfalls
- `agent_helpers.py` in the browser workspace is imported on EVERY browser call. A syntax error there breaks all calls until it is fixed. Write it with the file tool (read it first) rather than string-patching it with escaped JS.
- Inside helper functions, reach browser helpers through `import __main__ as M; M.goto_url(...)`. They are not in the helper module's globals.
