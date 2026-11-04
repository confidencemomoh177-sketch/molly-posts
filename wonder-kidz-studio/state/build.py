import json, subprocess, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import ITEMS
WK = '/home/claude/wk'
PDF = {'activity': '/home/claude/cozy/activity.pdf', 'coloring': '/home/claude/cozy/coloring.pdf'}
COVER = {'activity': '/home/claude/cozy/persona/wonderkidz_logo_1000.png', 'coloring': '/home/claude/cozy/cover_coloring.png'}
book = dict(primary="#C62033", secondary="#1C4A33", background="#FCF6EB", accent="#FFD257", cta="Link in bio", more=50, page_side=90)
tracks = sorted(os.listdir(f'{WK}/music'))
# interleave children/christmas tracks so neighbours sound different
kids = [t for t in tracks if t.startswith('children')]; xmas = [t for t in tracks if t.startswith('christmas')]
order = [x for pair in zip(xmas, kids + xmas[len(kids):]) for x in pair][:len(ITEMS)]
seen = []
for t in order:
    if t not in seen: seen.append(t)
order = (seen + [t for t in tracks if t not in seen])[:len(ITEMS)]
json.dump(book, open(f'{WK}/book.json', 'w'))
only = sys.argv[1:]
for n, it in enumerate(ITEMS):
    if only and it['key'] not in only: continue
    pre = 'a' if it['book'] == 'activity' else 'c'
    pg = f"{WK}/pages/{pre}-{it['pdf_page']}.png"
    if not os.path.exists(pg):
        subprocess.run(['pdftoppm', '-f', str(it['pdf_page']), '-l', str(it['pdf_page']), '-r', '200', '-png', '-singlefile', PDF[it['book']], pg[:-4]], check=True)
    item = {k: it[k] for k in ('num', 'tag', 'hook', 'inside_title', 'layers', 'facts', 'page_title', 'page_extra', 'more_title',
                                'pin_title', 'pin_sub', 'pin_cta', 'swipe_text', 'page_cut')}
    ph = f"{WK}/pages/photo-{pre}-{it['pdf_page']}.png"
    from PIL import Image as _I
    _im = _I.open(pg); _im.crop((0, 60, _im.width, 1960 if pre == 'a' else 1820)).save(ph)
    item.update(g_top=0.25, g_bottom=0.97, g_start=0.10)
    item.update(out=f"{WK}/posts/{n+1:02d}_{it['key']}", photo=ph, page=pg, subhook=it['sub'], cover=COVER[it['book']],
                page_top=120, music=f"{WK}/music/{order[n]}")
    if it.get('s4_sub'): item['s4_sub'] = it['s4_sub']
    json.dump(item, open(f"{WK}/item_{it['key']}.json", 'w'), ensure_ascii=False)
    r = subprocess.run(['python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_post.py'), f'{WK}/book.json', f"{WK}/item_{it['key']}.json"], capture_output=True, text=True)
    print(n + 1, it['key'], order[n], r.stdout.strip()[-60:], r.stderr[-400:])
