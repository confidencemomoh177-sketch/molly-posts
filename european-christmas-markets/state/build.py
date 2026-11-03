import json, subprocess, os, sys, re
from PIL import Image
sys.path.insert(0, '.')
from items import ITEMS, ORDER
SRC = '/home/claude/ecm/src'; PDF = f'{SRC}/book.pdf'
pages = open(f'{SRC}/book.txt').read().split('\f')
DPI = 200; S = DPI / 72

def find_page(head):
    for i, t in enumerate(pages[15:], 16):
        for ln in t.splitlines():
            if ' '.join(ln.split()).startswith(head): return i
    raise SystemExit('no page for ' + head)

def head_y(p, head):
    out = subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), '-bbox', PDF, '-'], capture_output=True, text=True).stdout
    words = re.findall(r'yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">([^<]*)<', out)
    hw = head.split()[:3]
    for k in range(len(words) - len(hw) + 1):
        if all(words[k + j][1].replace('&apos;', "'") == hw[j] for j in range(len(hw))):
            return float(words[k][0]) * S
    print('  (heading not located on page', p, head, ')'); return 150

def render(p):
    f = f'pages/p-{p:03d}.png'
    if not os.path.exists(f):
        subprocess.run(['pdftoppm', '-f', str(p), '-l', str(p), '-r', str(DPI), '-png', '-singlefile', PDF, f[:-4]], check=True)
    return Image.open(f).convert('RGB')

def page_image(head, key):
    p = find_page(head); y = head_y(p, head)
    a = render(p); hdr, ftr = 130, 2200 - 150
    top = max(hdr, int(y) - 40)
    need = 1320
    if a.height - 150 - top >= need:
        img = a.crop((0, top, a.width, top + need))
    else:   # stitch the next page under it
        b = render(p + 1)
        part1 = a.crop((0, top, a.width, ftr)); part2 = b.crop((0, hdr, b.width, hdr + need - part1.height))
        img = Image.new('RGB', (a.width, need), 'white'); img.paste(part1, (0, 0)); img.paste(part2, (0, part1.height))
    import numpy as np
    g = np.asarray(img.convert('L')); blank = (g.min(axis=1) > 235)
    run = 0
    for yy in range(300, len(blank)):
        run = run + 1 if blank[yy] else 0
        if run >= 220: img = img.crop((0, 0, img.width, yy - run + 60)); break
    out = f'pages/{key}.png'; img.save(out); return out, p

os.makedirs('pages', exist_ok=True)
tracks = sorted(os.listdir('/home/claude/ecm/music'))
book = json.load(open('book.json'))
only = sys.argv[1:]
for n, key in enumerate(ORDER):
    it = next(i for i in ITEMS if i['key'] == key)
    if only and key not in only: continue
    pg, p = page_image(it['head'], key)
    item = dict(num=n + 1, out=f'posts/{n+1:02d}_{key}', photo=f"{SRC}/img/i-{it['img']:03d}.png", page=pg,
                page_top=0, page_cut=1320, page_side=110,
                tag=it['tag'], hook=it['hook'], subhook=it['sub'], inside_title=it['inside'], layers=it['layers'],
                facts=it['facts'], page_extra=it['extra'], pin_title=it['pin_title'], pin_sub=it['pin_sub'],
                music='/home/claude/ecm/music/' + tracks[n % len(tracks)])
    json.dump(item, open(f'items_{key}.json', 'w'), ensure_ascii=False, indent=1)
    r = subprocess.run(['python3', '../make_post.py', 'book.json', f'items_{key}.json'], capture_output=True, text=True)
    print(n + 1, key, 'page', p, tracks[n % len(tracks)], r.stdout.strip(), r.stderr[-300:])
