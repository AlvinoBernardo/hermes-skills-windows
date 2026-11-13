import json,re,statistics
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
A=json.load(open("talking_all.json", encoding="utf-8"))
def txt(r): return ((r["hook"] or "")+" || "+(r["text_hook"] or "")).lower().replace("’","'").replace("*","u")
P={
 "is_it_possible": r"is it possible to",
 "dont_know_who_needs": r"i don'?t know who needs to hear this",
 "heres_how_to_actually": r"here'?s how to actually|how to actually",
 "every_level_view_jail": r"(every|4|four|3|three) (level|lvl)s? of (view jail|.*jail)",
 "i_cant_afford": r"i can'?t afford",
 "only_video_ever_need": r"only video you('| wi)ll ever need|only video you need",
 "if_youre_asian": r"if you'?re asian",
 "every_single_time": r"every single time",
 "fyou_money": r"f.ck.?you money|fuck you money|f-you money",
 "fear_judge": r"afraid.*judge|scared.*judge",
 "slump": r"out of a slump|biggest slumps?",
 "heres_how_much": r"here'?s how much",
 "cancelled": r"get(ting)? cancell?ed",
 "the_reason_your": r"the reason (why )?your",
 "day_n_series": r"(today'?s|today is) day \d+|day \d+ (of )?(road|learning)|road to \$",
 "pov": r"^pov|\|\| pov",
 "laying_in_bed": r"laying in bed|lying in bed",
 "everyone_will_tell": r"everyone will tell you",
 "apparently_if_you": r"apparently,? if you",
 "years_ago_i": r"^(two|three|four|five|\d) years ago",
 "spent_the_last_writing": r"spent the last .* writing down|i studied",
 "stop_caps": r"^stop |\|\| stop ",
 "hooks_in_60": r"in (60|sixty) seconds",
 "five_year_old": r"5.?y(ea)?r.?old|five.year.old",
 "speedrun": r"speedrun",
 "mindset_hack": r"mindset hack",
 "i_copied": r"i copied",
 "is_actually_good": r"is actually good",
 "league_of_legends": r"league of legends",
 "claude": r"claude",
 "this_is_your_sign": r"this is your sign",
 "if_you_want_to": r"^if you (want|wanna) to",
 "heres_how_i": r"^here'?s (exactly )?how i",
 "one_thing_you_need": r"(the )?one thing (you need|that)",
 "dropped_out": r"dropp?(ed|ing) out",
 "100k_month": r"\$?100,?(000|k) (a|per|/) ?month|\$100k/month",
}
res={}
for k,p in P.items():
    v=[r for r in A if re.search(p,txt(r))]
    if not v: continue
    o=[r["outlier"] for r in v]
    res[k]=v
    print(f"{k:24} n={len(v):3} viral={sum(x>=2 for x in o):3} ({100*sum(x>=2 for x in o)/len(v):3.0f}%) median={statistics.median(o):5.2f} flops<1={sum(x<1 for x in o)}")
json.dump({k:[r["id"] for r in v] for k,v in res.items()},open("hook_patterns_ids.json","w", encoding="utf-8"))
