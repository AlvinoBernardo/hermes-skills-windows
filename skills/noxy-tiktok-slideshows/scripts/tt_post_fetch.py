#!/usr/bin/env python3
"""Fetch TikTok post stats + all slideshow images without a browser.

Stdlib only: any python 3.8+ works (Mac: python3; Windows: `python` or the engine venv python.exe).

Usage: tt_post_fetch.py hrefs.json [outdir]
hrefs.json = list of https://www.tiktok.com/@user/photo/<id> (or /video/<id>) URLs.
Writes <outdir>/posts/<user>_<id>/{01.jpg..,meta.json}; cached posts are skipped,
so rerun after rate-limit errors.
"""
import urllib.request, re, json, os, sys, concurrent.futures as cf

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/129.0 Safari/537.36', 'Accept-Language': 'en-US,en;q=0.9'}

if hasattr(sys.stdout, 'reconfigure'):  # Windows console/pipe defaults to cp1252
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()


def fetch(href, outdir='.'):
    user = href.split('/@')[1].split('/')[0]
    pid = href.rstrip('/').split('/')[-1]
    out = os.path.join(outdir, 'posts', f'{user}_{pid}')
    if os.path.exists(out + '/meta.json'):
        return json.load(open(out + '/meta.json', encoding='utf-8'))
    # /video/ URL carries webapp.video-detail even for photo posts; /photo/ does not
    h = get(f'https://www.tiktok.com/@{user}/video/{pid}').decode('utf8', 'ignore')
    m = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', h, re.S)
    if not m:
        raise RuntimeError('no rehydration data (rate limited?) ' + href)
    it = json.loads(m.group(1))['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']
    os.makedirs(out, exist_ok=True)
    imgs = (it.get('imagePost') or {}).get('images', [])
    paths = []
    for i, im in enumerate(imgs[:20]):
        p = f'{out}/{i + 1:02d}.jpg'
        try:
            open(p, 'wb').write(get(im['imageURL']['urlList'][0]))
            paths.append(p)
        except Exception as e:
            print('img err', e)
    meta = dict(href=href, user=user, id=pid, desc=it.get('desc'), create=int(it['createTime']),
                stats=it.get('statsV2') or it.get('stats'), n=len(imgs),
                title=(it.get('imagePost') or {}).get('title'),
                music=(it.get('music') or {}).get('title'), paths=paths)
    json.dump(meta, open(out + '/meta.json', 'w', encoding='utf-8'), ensure_ascii=False)
    return meta


if __name__ == '__main__':
    hrefs = json.load(open(sys.argv[1], encoding='utf-8'))
    outdir = sys.argv[2] if len(sys.argv) > 2 else '.'
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {ex.submit(fetch, h, outdir): h for h in hrefs}
        for f in cf.as_completed(futs):
            try:
                m = f.result()
                print(m['user'], m['stats'].get('playCount'), m['n'])
            except Exception as e:
                print('ERR', futs[f], e)
