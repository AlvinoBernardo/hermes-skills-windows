#!/usr/bin/env python3
"""Build the deliverable: report.html (self-contained preview), report.md, posts.csv.

Usage: build_report.py <out_dir>
Reads <out_dir>/manifest.json (from fetch_*.py + prep_media.py) and <out_dir>/analysis.json (written by the agent):
{
  "summary": "2-4 sentence headline takeaway",
  "patterns": [{"title": "...", "detail": "...", "evidence": ["#01", "#04"]}],
  "winners_vs_flops": "paragraph",
  "ideas": [{"title": "...", "hook": "...", "format": "...", "why": "..."}],
  "posts": {"<id>": {"hook": "exact on-screen/spoken hook", "hook_type": "...", "format": "...",
                      "topic": "...", "structure": "...", "cta": "...", "why": "..."}}
}
"""
import base64, csv, html, io, json, shutil, statistics, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

out = Path(sys.argv[1]).expanduser()
man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
ana = json.loads((out / "analysis.json").read_text(encoding="utf-8")) if (out / "analysis.json").exists() else {}
pa = ana.get("posts", {})
posts = man["posts"]; top = [p for p in posts if p["view_rank"] <= man["top_n"]]
E = html.escape


def fmt(n):
    n = n or 0
    return f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.1f}K" if n >= 1e3 else str(n)


def day(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d") if ts else ""


def eng(p):
    return round(100 * (p["likes"] + p["comments"] + p["shares"] + p.get("saves", 0)) / p["views"], 2) if p["views"] else None


def thumb(rel, w=420):
    if not rel or not (out / rel).exists(): return ""
    r = subprocess.run([shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg", "-v", "error", "-i", str(out / rel), "-vf", f"scale={w}:-2",
                        "-q:v", "5", "-f", "image2", "-"], capture_output=True)
    return "data:image/jpeg;base64," + base64.b64encode(r.stdout).decode() if r.stdout else ""


# CSV of the full pool
with open(out / "posts.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["view_rank", "in_top", "platform", "kind", "date", "views", "views_estimated", "likes", "comments", "shares",
                "saves", "engagement_%", "duration_s", "slides", "url", "hook", "hook_type", "format", "topic", "caption"])
    for p in posts:
        a = pa.get(p["id"], {})
        w.writerow([p["view_rank"], p["view_rank"] <= man["top_n"], p["platform"], p.get("kind", ""), day(p["timestamp"]),
                    p["views"], p.get("views_estimated", False), p["likes"], p["comments"], p["shares"], p.get("saves", 0),
                    eng(p), p.get("duration"), p.get("slides"), p["url"], a.get("hook", ""), a.get("hook_type", ""),
                    a.get("format", ""), a.get("topic", ""), (p.get("caption") or "").replace("\n", " ")])

views = [p["views"] for p in posts]
med = statistics.median(views) if views else 0
kinds = {}
for p in top: kinds[p.get("kind", "?")] = kinds.get(p.get("kind", "?"), 0) + 1
stats = [("Posts scanned", len(posts)), ("Analyzed", len(top)), ("Followers", fmt(man.get("followers"))),
         ("Median views (all)", fmt(med)), ("#1 views", fmt(top[0]["views"] if top else 0)),
         ("Top-N mix", " · ".join(f"{v} {k}" for k, v in kinds.items()))]

cards = []
for p in top:
    a = pa.get(p["id"], {})
    img = thumb(p.get("hook_sheet") or p.get("sheet"))
    mult = f"{p['views']/med:.1f}× median" if med else ""
    rows = "".join(f"<dt>{E(k)}</dt><dd>{E(str(a[k2]))}</dd>" for k, k2 in
                   [("Hook", "hook"), ("Hook type", "hook_type"), ("Format", "format"), ("Topic", "topic"),
                    ("Structure", "structure"), ("CTA", "cta"), ("Why it worked", "why")] if a.get(k2))
    tr = f"<details><summary>Transcript</summary><p>{E(p['transcript'])}</p></details>" if p.get("transcript") else ""
    cap = f"<details><summary>Caption</summary><p>{E(p.get('caption') or '')}</p></details>" if p.get("caption") else ""
    cards.append(f"""<article class=card><div class=thumb>{f'<img src="{img}">' if img else ''}</div><div class=body>
<h3>#{p['view_rank']:02d} · {fmt(p['views'])}{'*' if p.get('views_estimated') else ''} views <span class=m>{mult}</span></h3>
<p class=meta>{E(p.get('kind',''))}{f" · {p['duration']}s" if p.get('duration') and p.get('kind')=='video' else ''}{f" · {p['slides']} slides" if p.get('slides') else ''} · {day(p['timestamp'])} · ♥ {fmt(p['likes'])} · 💬 {fmt(p['comments'])} · ↗ {fmt(p['shares'])} · eng {eng(p) or '–'}% · <a href="{E(p['url'])}">open</a></p>
<dl>{rows}</dl>{tr}{cap}</div></article>""")

pat = "".join(f"<li><b>{E(x['title'])}</b> — {E(x['detail'])} <span class=m>{E(', '.join(x.get('evidence', [])))}</span></li>" for x in ana.get("patterns", []))
ideas = "".join(f"<li><b>{E(x['title'])}</b><br>Hook: “{E(x.get('hook',''))}” · Format: {E(x.get('format',''))}<br><span class=m>{E(x.get('why',''))}</span></li>" for x in ana.get("ideas", []))
title = f"@{man['handle']} — {man['platform'].title()} viral breakdown"
doc = f"""<!doctype html><html><head><meta charset=utf-8><title>{E(title)}</title><style>
body{{font:15px/1.5 -apple-system,system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;color:var(--foreground,#111)}}
h1{{margin:0 0 4px}} .m{{color:var(--muted-foreground,#777);font-size:13px}}
.stats{{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}} .stats div{{border:1px solid var(--border,#ddd);border-radius:10px;padding:8px 12px}}
.stats b{{display:block;font-size:18px}} .card{{display:flex;gap:16px;border:1px solid var(--border,#ddd);border-radius:12px;padding:12px;margin:12px 0}}
.thumb img{{width:300px;border-radius:8px}} .body{{flex:1;min-width:0}} h3{{margin:0}} .meta{{margin:4px 0 8px;font-size:13px}}
dl{{display:grid;grid-template-columns:110px 1fr;gap:4px 10px;margin:0}} dt{{font-weight:600}} dd{{margin:0}}
details{{margin-top:6px;font-size:13px}} li{{margin:6px 0}} section{{margin:24px 0}}
@media(max-width:700px){{.card{{flex-direction:column}}.thumb img{{width:100%}}}}</style></head><body>
<h1>{E(title)}</h1><p class=m>Last {man['pool_size']} posts, top {man['top_n']} by {E(man['rank_metric'])} · fetched {day(man['fetched_at'])}{' · * = estimated from likes' if any(p.get('views_estimated') for p in top) else ''}</p>
<div class=stats>{''.join(f'<div><span class=m>{E(k)}</span><b>{E(str(v))}</b></div>' for k, v in stats)}</div>
{f"<section><h2>Takeaway</h2><p>{E(ana['summary'])}</p></section>" if ana.get('summary') else ''}
{f"<section><h2>Patterns in the winners</h2><ul>{pat}</ul></section>" if pat else ''}
{f"<section><h2>Winners vs flops</h2><p>{E(ana['winners_vs_flops'])}</p></section>" if ana.get('winners_vs_flops') else ''}
{f"<section><h2>Ideas to steal</h2><ol>{ideas}</ol></section>" if ideas else ''}
<section><h2>Top {man['top_n']} posts</h2>{''.join(cards)}</section></body></html>"""
(out / "report.html").write_text(doc, encoding="utf-8")

md = [f"# {title}", "", f"Last {man['pool_size']} posts, top {man['top_n']} by {man['rank_metric']}.", ""]
if ana.get("summary"): md += ["## Takeaway", ana["summary"], ""]
if ana.get("patterns"): md += ["## Patterns", *[f"- **{x['title']}** — {x['detail']} ({', '.join(x.get('evidence', []))})" for x in ana["patterns"]], ""]
if ana.get("winners_vs_flops"): md += ["## Winners vs flops", ana["winners_vs_flops"], ""]
if ana.get("ideas"): md += ["## Ideas", *[f"{i}. **{x['title']}** — hook: “{x.get('hook','')}” · {x.get('format','')} — {x.get('why','')}" for i, x in enumerate(ana["ideas"], 1)], ""]
md += ["## Top posts", "| # | Views | Kind | Hook | Why |", "|---|---|---|---|---|"]
md += [f"| {p['view_rank']} | {fmt(p['views'])} | {p.get('kind','')} | {pa.get(p['id'],{}).get('hook','').replace('|','/')} | {pa.get(p['id'],{}).get('why','').replace('|','/')} |" for p in top]
(out / "report.md").write_text("\n".join(md), encoding="utf-8")
print("wrote", out / "report.html", out / "report.md", out / "posts.csv")
