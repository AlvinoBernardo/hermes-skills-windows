# Six-package batch: BRIEF.md + worker prompt template

Use for the standard "slideshows for all my accounts" batch (2 @EmilyF1tness, 2 @emma_weightgoals, 2 @noxy.app). Fill the angle-bracket slots from the ledgers, write the brief, then spawn all six workers in ONE delegate_task call.

## Parent setup (in order)
1. Before announcing the lineup, read `references/account-performance.md`, then the top of `Finished-slides/SESSION-HANDOFF.md`, `male-format-rotation.json` `variant_history`, `female-format-rotation.json` per-account exclusions and recent history, and `hook-rotation.json` (Emma's latest restart and subsequent history). Standard scope is six packages, not one per account.
2. Select formats from the newest feedback, not an older template or bag:
   - Emily: use the manga workout test direction with varied topics and structures unless newer feedback overrides it. Food swaps and illustrated weight-loss tips were reported inconsistent; do not silently revert to them as proven winners. List recent topics to avoid and mark untested directions in posting notes.
   - Emma: one girlies-gym-know plus one classic working-female or sasha-diary. Source new aesthetic real Pinterest photographs; the older library is not an automatic fallback. Pick a classic hook unused in her current cycle; the girlies format keeps its canonical opener. Preserve the unused bag rather than consuming draws that were not selected.
   - Male: two different fox-manga variants, neither equal to the last logged variant (A is retired).
3. `mkdir Finished-slides/four-female-two-male-<NN>/`, concatenate the last four batches' `_claims.jsonl` into `_prior_claims_<a>-<b>.jsonl`, create an empty `_claims.jsonl`.
4. Dump the full skill text to `~/.hermes/cache/scratch/skill_noxy.md` (the SKILL.md is ~100 KB and skill_view spills it) and give workers that path so they can page it with read_file.
5. If two or more packages share a NEW illustrated character (e.g. emily-manga-workout), generate ONE shared anchor yourself first, inspect it, save it to `<batch>/_shared/`, and name it in the brief as the `image_url` for every generation. Parallel workers inventing the character independently produce different-looking girls across posts.
6. Write BRIEF.md (shape below), save the task list as `_tasks.json`, spawn. When the user asks for music, add ONE dedicated music-research task to the same spawn (all packages, writes `<batch>/MUSIC.json` + MUSIC.txt per `references/music-picks.md`). A single agent fetches TikTok post data sequentially; per-worker music research runs in parallel and gets rate limited.
7. A pasted multi-account spec plus an extra ask ("and 2 for noxy") is one batch: add the extra packages as workers in the same spawn with their own brief section, pick variants from the male ledger as usual, and deliver each account group in its own tidy folder.

## BRIEF.md shape
```
# Batch<NN> • <date>
User request: "<verbatim>". Standard split. Review deliverables only. Never publish or schedule. No approval gates.
Batch root: <abs path>. Each worker writes ONLY inside its package subfolder. Parent owns ledgers, review, delivery, master ZIP.

## Assigned packages (draws are final)
1. emily-01 / @EmilyF1tness / <format> / `<hook>` / <size, slides>. Latest kit: <path>. Used scenarios to avoid: <list>.
2. emily-02 / ...
3. emma-01 / @emma_weightgoals / <format> / `<hook>` / 1080x1920. Latest build: <path>. Noxy placement rule for that format.
4. emma-02 / ...
5. male-01 / @noxy.app / fox-manga-workout variant <X> / <topic> / <slides>. Noxy slide in the MIDDLE.
6. male-02 / ... (different variant and topic)
Previous male variants: <list>.

## Production contracts
slides/ (numbered PNGs only), preview.jpg, caption.txt (public text only), POSTING.txt, manifest.json (hook, format, account, slides, sources with path/pin/sha256, generated assets with prompts, Noxy slide index), <package>.zip tested, _source/.
Aesthetics first for female photos, dHash-check against prior claims + _claims.jsonl, append picks to _claims.jsonl.
Real Noxy screen/card only. Never call Noxy free. No invented results. No dashes or semicolons in copy. Pinterest rights unverified. AI disclosure in captions for Emily/male. NO AI imagery for Emma except a green-screen phone holding the real screen.
```

## Common worker prompt (prepend to every task's context)
```
You are a build worker for the user's Noxy TikTok slideshow batch. Noxy is the user's iOS calorie tracker (orange fox icon). It is NOT free.
FIRST: read <batch>/BRIEF.md and load skill noxy-tiktok-slideshows (full text saved at <scratch>/skill_noxy.md, page it with read_file). Load the references named for your format.
Work ONLY inside your package folder. Do NOT edit ledgers or other packages. Do not ask questions or stop for approval. Never post. Never fabricate: report failures.
No dashes or semicolons in slide copy or captions. caption.txt is public text only.
Run kits with `env -u PYTHONPATH -u PYTHONHOME /usr/bin/python3` if numpy/scipy fail (Windows: `C:/Users/<you>/IkkimiAssets/engine/.venv/Scripts/python.exe` from `terminal`).
Visual QA with vision_analyze on preview + critical full-size slides (new scratch filename per round). Check phone-size readability as well as glyph bounds: bounds cannot detect text crossing a bowl, shoe, equipment lettering or textured photo. Keep the right 15% and caption zone clear. For photos, inspect actual final crops for sharpness, quiet text space and literal subject fit; a pasta pot does not demonstrate measuring oil. A technically fresh photo still fails if murky or snapshot-like. For illustrated covers, make the hero large enough to read at thumbnail size and ensure the pictured load/support matches the hook. Check anatomy and movement-frame differences before typesetting.
Outputs: slides/, preview.jpg, caption.txt, POSTING.txt, manifest.json, <package>.zip (tested), _source/.
Final answer: path, slide count, hook, one line per slide, Noxy slide index, AI vs real assets, known weaknesses.
```
Then add package specifics: the exact kit paths to reuse, the content mechanism (e.g. six named everyday mistakes with fixes), placement of Noxy, cover rules, and for Emma the parallel-claims coordination line (read `_claims.jsonl` before locking, append immediately after).

## After workers return
1. Read manifests and inspect every preview yourself; verify counts, real Noxy placement and exact source hashes. Compare both Emma packages together for repeated photos and visual monotony.
2. Run one independent read-only Claude critic per manga package, fox AND Emily. Also review Emma photography against the aesthetics gate. Load `claude-code` and check authentication before invoking `claude -p "<review brief>" --model sonnet --tools 'Read,Glob' --allowedTools 'Read,Glob' --max-turns 24 --output-format json --no-session-persistence` in the batch directory. Independent subprocesses can run concurrently. Save each round separately and inspect `subtype`, `result` and `modelUsage`; a builder's self-check is not independent Claude review.
3. Give critics actual slide paths, caption, posting notes, and reference images, not only analysis prose. Ask separately whether the work is creatively ready (conditional on rights clearance) and whether its craft could compete with the reference posts. Treat scores and the ~10k comparison as subjective, never a forecast. Include the fixed brief: orange fox ink on lavender, Emily ink on blush, genuine speaker app-use already confirmed, real Noxy in the middle. These constraints prevent critics from proposing an unwanted redesign or moving the app near the end.
4. Consolidate genuine blockers and cheap polish into one fix worker per package. Require changed-slide inspection, updated manifests/hashes, rebuilt previews and byte-tested ZIPs. Re-review packages that received NO against their previous blockers and current images; do not accept a fix report alone or force a positive judgment. Leave passing packages untouched.
5. Build the delivery while reviews run if useful, but label it draft and do not advance completion ledgers yet. After fixes pass, rebuild from the final files, verify all archive member bytes and viewer paths, then update format/hook/variant ledgers and SESSION-HANDOFF.md. Remove stale 'parent critic pending' notes only after the review is complete.
