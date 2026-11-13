"""Build the tidy delivery folder for a multi-package slideshow batch.

Copy, edit BATCH / OUT / PKGS, run with python3 (Mac) or the engine venv python.exe (Windows, has PIL).
Root defaults to ~/Desktop/Noxy; override with env NOXY_ROOT. Expects each package folder to hold
slides/*.png, preview.jpg, caption.txt, POSTING.txt, manifest.json (key 'hook').
Produces OUT/<NN-Name>/ (slides, _preview.jpg, caption, POSTING, own ZIP), a master
_preview-all-six.jpg, _preview.html viewer (contain-fit, prev/next, package select),
POSTING.txt, content.json and a tested master ZIP beside OUT (individual ZIPs excluded).
"""
import hashlib, json, os, shutil, sys, zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(os.environ.get('NOXY_ROOT') or Path.home() / 'Desktop' / 'Noxy')
BATCH = ROOT / 'Finished-slides' / 'four-female-two-male-NN'
OUT = ROOT / 'Noxy-YYYY-MM-DD-slideshows-batchNN'
PKGS = [  # (package folder, delivery name, account, format label)
    ('emily-01', '01-Emily-Name', '@EmilyF1tness', 'format'),
    ('emma-01', '03-Emma-Name', '@emma_weightgoals', 'format'),
    ('male-01', '05-Male-Name', '@noxy.app', 'format'),
]
if hasattr(sys.stdout, 'reconfigure'):  # Windows pipes default to cp1252; hooks contain emoji
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
content, thumbs = [], []
for pkg, name, acct, fmt in PKGS:
    src, d = BATCH / pkg, OUT / name
    d.mkdir()
    files = []
    for s in sorted((src / 'slides').glob('*.png')):
        t = d / s.name
        shutil.copy2(s, t)
        assert sha(s) == sha(t)
        files.append(t)
    shutil.copy2(src / 'preview.jpg', d / '_preview.jpg')
    for f in ('caption.txt', 'POSTING.txt'):
        shutil.copy2(src / f, d / f)
    hook = json.loads((src / 'manifest.json').read_text(encoding='utf-8')).get('hook') or ''
    if isinstance(hook, dict):
        hook = hook.get('text') or json.dumps(hook)
    z = d / f'{name}.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files + [d / 'caption.txt', d / 'POSTING.txt']:
            zf.write(f, f'{name}/{f.name}')
    with zipfile.ZipFile(z) as zf:
        assert zf.testzip() is None
    content.append(dict(package=pkg, folder=name, account=acct, format=fmt, hook=hook,
                        slides=[f.name for f in files],
                        size=sorted({Image.open(f).size for f in files}),
                        sha256={f.name: sha(f) for f in files}))
    thumbs.append(files)

TH, rows = 300, []
for files in thumbs:
    ims = [Image.open(f).convert('RGB') for f in files]
    ims = [im.resize((int(im.width * TH / im.height), TH)) for im in ims]
    row = Image.new('RGB', (sum(i.width for i in ims) + 8 * (len(ims) + 1), TH + 16), (24, 24, 24))
    x = 8
    for i in ims:
        row.paste(i, (x, 8)); x += i.width + 8
    rows.append(row)
sheet = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows)), (24, 24, 24))
y = 0
for r in rows:
    sheet.paste(r, (0, y)); y += r.height
sheet.save(OUT / '_preview-all-six.jpg', quality=88)

data = [dict(name=c['folder'], hook=c['hook'], account=c['account'],
             slides=[f"{c['folder']}/{s}" for s in c['slides']]) for c in content]
html = """<!doctype html><meta charset=utf-8><title>Noxy slideshows</title>
<style>body{font-family:-apple-system,'Segoe UI',sans-serif;background:#111;color:#eee;margin:20px}select,button{font-size:16px;margin:4px}
#v{display:flex;justify-content:center;align-items:center;height:80vh}#v img{max-height:100%;max-width:100%;object-fit:contain}</style>
<div><select id=p></select><button id=pr>Previous</button><button id=nx>Next</button><span id=c></span> <a id=fl target=_blank>full resolution</a></div>
<div id=h></div><div id=v><img id=im></div>
<script>const D=__DATA__;let p=0,i=0;const sel=document.getElementById('p');
D.forEach((d,k)=>{let o=document.createElement('option');o.value=k;o.textContent=d.name;sel.appendChild(o)});
function r(){const d=D[p];const s=d.slides[i];im.src=s;fl.href=s;c.textContent=` ${i+1} / ${d.slides.length}`;h.textContent=d.account+'  ·  '+d.hook}
sel.onchange=()=>{p=+sel.value;i=0;r()};pr.onclick=()=>{const n=D[p].slides.length;i=(i-1+n)%n;r()};nx.onclick=()=>{i=(i+1)%D[p].slides.length;r()};
document.onkeydown=e=>{if(e.key=='ArrowRight')nx.onclick();if(e.key=='ArrowLeft')pr.onclick()};r();</script>"""
(OUT / '_preview.html').write_text(html.replace('__DATA__', json.dumps(data)), encoding='utf-8')

lines = [f'NOXY SLIDESHOWS {OUT.name}. Review drafts, nothing posted.', '']
lines += [f"{c['folder']}  {c['account']}  {c['format']}  {len(c['slides'])} slides  hook: {c['hook']}" for c in content]
lines += ['', 'Each folder: numbered slides in order, caption.txt, POSTING.txt, its own ZIP.',
          'Turn on the TikTok AI label for posts with AI art. Pin a comment with the app name.',
          'Pinterest photo rights are unverified. Never call Noxy free.']
(OUT / 'POSTING.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
(OUT / 'content.json').write_text(json.dumps(content, indent=1), encoding='utf-8')

master = OUT.parent / (OUT.name + '.zip')
master.unlink(missing_ok=True)
with zipfile.ZipFile(master, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(OUT.rglob('*')):
        if f.is_file() and f.suffix != '.zip':
            zf.write(f, f'{OUT.name}/{f.relative_to(OUT)}')
with zipfile.ZipFile(master) as zf:
    assert zf.testzip() is None
    n_png = sum(n.endswith('.png') for n in zf.namelist())
print('packages', len(content), 'slides', sum(len(c['slides']) for c in content), 'master pngs', n_png)
for c in content:
    print(c['folder'], len(c['slides']), c['size'], '|', c['hook'])
