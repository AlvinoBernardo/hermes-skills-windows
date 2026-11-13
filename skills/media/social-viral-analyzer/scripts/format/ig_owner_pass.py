#!/usr/bin/env python3
"""Owner filter: the IG /reels/ tab also returns tagged, collab and suggested reels from OTHER creators.

Usage: ig_owner_pass.py <workdir> <handle>
Reads list_ig_<handle>.json (+ media_info/<code>.json when present, which is authoritative) and writes
owners.json = {code: {"owner": u, "coauthors": [...], "keep": bool, "why": "..."}} plus a summary line.
keep = owner is the creator, OR the creator is listed as a coauthor (collab posts count as theirs).
Downstream scripts (build_format_table.py) drop keep=false rows.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load, save  # noqa: E402


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    W = Path(sys.argv[1]).expanduser(); h = sys.argv[2].lstrip("@").lower()
    lst = load(W / f"list_ig_{h}.json") or sys.exit("list file missing")
    res, dropped = {}, []
    for e in lst["entries"]:
        info = load(W / "media_info" / f"{e['code']}.json") or {}
        owner = ((info.get("user") or info.get("owner") or {}).get("username") or e.get("owner") or "").lower()
        co = [c.get("username", "").lower() for c in info.get("coauthor_producers") or []] or \
             [c.lower() for c in e.get("coauthors") or []]
        if owner == h:
            keep, why = True, "owner"
        elif h in co:
            keep, why = True, f"coauthor (owner {owner})"
        elif not owner:
            keep, why = True, "owner unknown - kept"
        else:
            keep, why = False, f"other creator @{owner}"
        res[e["code"]] = {"owner": owner, "coauthors": co, "keep": keep, "why": why}
        if not keep:
            dropped.append(f"{e['code']} (@{owner})")
    save(W / "owners.json", res)
    print(f"owners.json: {len(res)} reels, kept {len(res) - len(dropped)}, dropped {len(dropped)}")
    for d in dropped[:20]:
        print("  dropped", d)


if __name__ == "__main__":
    main()
