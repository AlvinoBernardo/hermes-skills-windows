#!/usr/bin/env python3
"""Sequential music-struct fetch for TikTok posts (no browser). Stdlib only: any python 3.8+ works
(Mac: python3; Windows: `python` or the engine venv python.exe).
Usage: tt_music_fetch.py in.json out.json
in.json = list of post URLs or {"url":..., "tag":...}. Results cached in out.json (rerun skips done ids).
Per post: views, photo flag, desc, music {title, author, id, original, duration}. 1.6 s gap between requests.
"""
import urllib.request, re, json, os, sys, time

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/129.0 Safari/537.36', 'Accept-Language': 'en-US,en;q=0.9'}

if hasattr(sys.stdout, 'reconfigure'):  # Windows console/pipe defaults to cp1252
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()


def fetch(url):
    user = url.split('/@')[1].split('/')[0]
    pid = url.rstrip('/').split('?')[0].split('/')[-1]
    h = get(f'https://www.tiktok.com/@{user}/video/{pid}').decode('utf8', 'ignore')
    m = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', h, re.S)
    if not m:
        raise RuntimeError('no rehydration data')
    vd = json.loads(m.group(1))['__DEFAULT_SCOPE__'].get('webapp.video-detail', {})
    it = (vd.get('itemInfo') or {}).get('itemStruct')
    if not it:
        raise RuntimeError('no itemStruct status=%s' % vd.get('statusCode'))
    mu = it.get('music') or {}
    st = it.get('statsV2') or it.get('stats') or {}
    return dict(url=url, user=user, id=pid, desc=(it.get('desc') or '')[:160],
                create=int(it.get('createTime', 0)), views=st.get('playCount'),
                photo=bool(it.get('imagePost')),
                music=dict(title=mu.get('title'), author=mu.get('authorName'), id=mu.get('id'),
                           original=mu.get('original'), duration=mu.get('duration'),
                           isCopyrighted=mu.get('isCopyrighted'), is_commerce_music=mu.get('is_commerce_music'),
                           playUrl=mu.get('playUrl')))


if __name__ == '__main__':
    items = json.load(open(sys.argv[1], encoding='utf-8'))
    out = sys.argv[2]
    res = json.load(open(out, encoding='utf-8')) if os.path.exists(out) else {}
    for x in items:
        url = x if isinstance(x, str) else x['url']
        tag = '' if isinstance(x, str) else x.get('tag', '')
        key = url.rstrip('/').split('?')[0].split('/')[-1]
        if key in res and 'music' in res[key]:
            continue
        for attempt in range(2):
            try:
                r = fetch(url); r['tag'] = tag
                res[key] = r
                print(r['user'], r['views'], r['music']['title'], '|', r['music']['author'], r['music']['id'], flush=True)
                break
            except Exception as e:
                print('ERR', url, e, flush=True)
                time.sleep(4)
        json.dump(res, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        time.sleep(1.6)
