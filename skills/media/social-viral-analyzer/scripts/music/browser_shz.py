# exec() inside browser_exec on an amp.shazam.com tab. POSTs local signatures from the cloud browser IP.
import json, os, time, uuid

D = os.path.expanduser('~/.hermes/cache/scratch/mm90')
SIGS, RES = D + '/sigs.json', D + '/shz_browser.json'


def _post1(body):
    url = (f"https://amp.shazam.com/discovery/v5/en-US/US/iphone/-/tag/{str(uuid.uuid4()).upper()}/{str(uuid.uuid4()).upper()}"
           "?sync=true&webv3=true&sampling=true&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3")
    code = ("(async()=>{const ac=new AbortController();setTimeout(()=>ac.abort(),4000);try{const r=await fetch(%s,{method:'POST',signal:ac.signal,headers:{'Content-Type':'application/json'},body:%s});"
            "const t=await r.text();return JSON.stringify({status:r.status,text:t})}catch(e){return JSON.stringify({status:0,text:String(e)})}})()"
            % (json.dumps(url), json.dumps(json.dumps(body))))
    r = json.loads(js(code))
    if r['status'] != 200:
        return {'error': f"http {r['status']} {r['text'][:80]}"}
    j = json.loads(r['text'])
    t = j.get('track') or {}
    m = (j.get('matches') or [{}])[0] if j.get('matches') else {}
    meta = {}
    for sec in t.get('sections', []) or []:
        for md in sec.get('metadata', []) or []:
            meta[md.get('title')] = md.get('text')
    apple = None
    for a in ((t.get('hub') or {}).get('actions') or []):
        if a.get('type') == 'applemusicplay': apple = a.get('id')
    return {'title': t.get('title'), 'artist': t.get('subtitle'), 'key': t.get('key'), 'apple_id': apple,
            'album': meta.get('Album'), 'released': meta.get('Released'),
            'song_offset_s': m.get('offset'), 'timeskew': m.get('timeskew'), 'frequencyskew': m.get('frequencyskew')}


def _post(body):
    for i in range(4):
        h = _post1(body)
        e = h.get('error') or ''
        if not (e.startswith('http 429') or e.startswith('http 0')):
            return h
        time.sleep(15 * (i + 1))
    return h


def run(budget_s=1500, gap=2.5):
    t0 = time.time()
    sigs = json.load(open(SIGS, encoding="utf-8"))
    res = json.load(open(RES, encoding="utf-8")) if os.path.exists(RES) else {}
    done = 0
    for code, v in sigs.items():
        for it in v['items']:
            k = f"{code}|{it['kind']}|{it['start']}"
            if k in res and not res[k].get('error'):
                continue
            if time.time() - t0 > budget_s:
                json.dump(res, open(RES, 'w', encoding="utf-8"), ensure_ascii=False, indent=1)
                print('budget stop', done); return
            h = _post(it['body']); h.update(code=code, kind=it['kind'], start=it['start'])
            res[k] = h; done += 1
            if done % 10 == 0:
                json.dump(res, open(RES, 'w', encoding="utf-8"), ensure_ascii=False, indent=1)
            time.sleep(gap)
    json.dump(res, open(RES, 'w', encoding="utf-8"), ensure_ascii=False, indent=1)
    print('ALL_DONE', done, 'total', len(res))
