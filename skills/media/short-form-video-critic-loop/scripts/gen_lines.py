#!/usr/bin/env python3
"""Queue per-line Voicebox generations (lines x seeds x profiles) and collect finished WAVs.
usage: python gen_lines.py OUTDIR PROFILE_ID[,PROFILE_ID2] SEEDS(comma)   (reads ./lines.json)
lines.json: [{"id":"s01","text":"...","gap":0.3}, ...]  gap = silence after the line when assembling.
Outputs OUTDIR/<profile6>_<lineid>_<seed>.wav. Resumable: jobs.json records queued ids."""
import json, sys, time, urllib.request, sqlite3, os, shutil
OUT, PROFILES, SEEDS = sys.argv[1], sys.argv[2].split(','), [int(s) for s in sys.argv[3].split(',')]
os.makedirs(OUT, exist_ok=True)
VB = os.path.expanduser('~/Library/Application Support/sh.voicebox.app')
API = 'http://localhost:17493'
lines = json.load(open('lines.json'))
jobs = json.load(open(f'{OUT}/jobs.json')) if os.path.exists(f'{OUT}/jobs.json') else {}
for prof in PROFILES:
    for ln in lines:
        for sd in SEEDS:
            key = f"{prof[:6]}_{ln['id']}_{sd}"
            if key in jobs: continue
            body = dict(profile_id=prof, text=ln['text'], engine='qwen', model_size='1.7B', seed=sd, normalize=True, max_chunk_chars=800)
            req = urllib.request.Request(f'{API}/generate', data=json.dumps(body).encode(), headers={'content-type': 'application/json'})
            jobs[key] = json.load(urllib.request.urlopen(req, timeout=60))['id']
json.dump(jobs, open(f'{OUT}/jobs.json', 'w'), indent=0)
print('queued', len(jobs), flush=True)
t0 = time.time()
while True:
    db = sqlite3.connect(f'{VB}/voicebox.db')
    rows = {r[0]: r[1:] for r in db.execute('select id,status,audio_path,error from generations')}
    db.close()
    done = failed = 0
    for key, gid in jobs.items():
        st, ap, _ = rows.get(gid, ('?', None, None))
        if st == 'completed':
            done += 1
            dst = f'{OUT}/{key}.wav'
            if not os.path.exists(dst): shutil.copy(f'{VB}/{ap}', dst)
        elif st == 'failed':
            failed += 1
    print(f'{int(time.time()-t0)}s done {done}/{len(jobs)} failed {failed}', flush=True)
    if done + failed >= len(jobs) or time.time() - t0 > 1700: break
    time.sleep(20)
