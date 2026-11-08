"""Build week-2 posts from items_w2.py and write calendar_w2.json.
Usage: python3 build_w2.py [key ...]"""
import json, subprocess, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from items_w2 import ITEMS, SHORT
from PIL import Image
WK = '/home/claude/wk'; REPO = os.path.dirname(HERE)
PDF = {'activity': '/home/claude/cozy/activity.pdf', 'coloring': '/home/claude/cozy/coloring.pdf'}
COVER = {'activity': '/home/claude/cozy/persona/wonderkidz_logo_1000.png', 'coloring': '/home/claude/cozy/cover_coloring.png'}
book = dict(primary="#C62033", secondary="#1C4A33", background="#FCF6EB", accent="#FFD257", cta="Link in bio", more=50, page_side=90)
json.dump(book, open(f'{WK}/book.json', 'w'))
tracks = sorted(os.listdir(f'{WK}/music'))
# start the rotation away from the tracks used last at the end of week 1
music = [tracks[(i * 4 + 3) % len(tracks)] for i in range(len(ITEMS))]
start = datetime.date(2026, 11, 9); times = ["09:00", "13:00", "20:00"]
os.makedirs(f'{WK}/w2', exist_ok=True); os.makedirs(f'{WK}/pages', exist_ok=True)
only = sys.argv[1:]
cal = []
for n, it in enumerate(ITEMS):
    pdfp = it['pdf_page'] if it['kind'] == 'A' else 2 * it['num'] + 7
    pre = 'a' if it['book'] == 'activity' else 'c'
    pg = f"{WK}/pages/{pre}-{pdfp}.png"
    if not os.path.exists(pg):
        subprocess.run(['pdftoppm', '-f', str(pdfp), '-l', str(pdfp), '-r', '200', '-png', '-singlefile', PDF[it['book']], pg[:-4]], check=True)
    ph = f"{WK}/pages/photo-{pre}-{pdfp}.png"
    im = Image.open(pg).convert('RGB'); im = im.crop((0, 60, im.width, 1960 if pre == 'a' else 1820))
    if it.get('pad'):
        nh = int(im.width / 0.5625); c = Image.new('RGB', (im.width, nh), 'white'); c.paste(im, (0, int((nh - im.height) * 0.35))); im = c
        ph = ph.replace('.png', '-pad.png')
    im.save(ph)
    out = f"{WK}/w2/{n+1:02d}_{it['key']}"
    keys = ('num', 'tag', 'hook', 'inside_title', 'layers', 'facts', 'page_title', 'page_extra', 'more_title',
            'pin_title', 'pin_sub', 'pin_cta', 'swipe_text', 'page_cut')
    item = {k: it[k] for k in keys}
    item.update(g_top=0.25, g_bottom=0.97, g_start=0.10, out=out, photo=ph, page=pg, cover=COVER[it['book']],
                page_top=120, music=f"{WK}/music/{music[n]}", subhook=it.get('subhook', it.get('sub', '')))
    if it.get('s4_sub'): item['s4_sub'] = it['s4_sub']
    if it['kind'] == 'C':
        item = {**book, **item}
        cp = f"{REPO}/colored_pages/{it['key']}"
        item.update(page_photo=ph, colored=f"{cp}_colored.png", lines=f"{cp}_lines.png",
                    sub=f"Page {it['num']} of 50 · swipe to watch it fill in", half_title=it['half_title'],
                    full_title=it['full_title'], full_sub=it['full_sub'])
    jf = f"{WK}/item_w2_{it['key']}.json"; json.dump(item, open(jf, 'w'), ensure_ascii=False)
    if not only or it['key'] in only:
        cmd = ['python3', f'{HERE}/make_post.py', f'{WK}/book.json', jf] if it['kind'] == 'A' else ['python3', f'{HERE}/color_post.py', jf]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(n + 1, it['key'], music[n], r.stdout.strip()[-40:], r.stderr[-300:])
    day = start + datetime.timedelta(days=n // 3); t = times[n % 3]
    tags = it['tags']
    tt = f"{it['tt']}\n{'Free printables' if it['book']=='activity' else 'Coloring book + free printables'} in bio. " + " ".join(tags[:4] + ["#christmaswithkids"])
    extra = ["#christmasactivitiesforkids", "#screenfreekids", "#kidsactivities" if "#kidsactivities" not in tags else "#preschoolactivities"]
    ig = it['ig'] + "\n\n" + " ".join(tags + extra)
    ytd = f"{it['ytd']}\n🎁 Free Christmas printables + our coloring book: {SHORT}\n#christmasactivities #kidsactivities #shorts"
    row = dict(n=n + 1, key=it['key'], kind=it['kind'], book=it['book'], date=str(day), time=t, timezone="America/New_York",
               hook_type=it['hook_type'], hook=it['hook'], music=music[n], out=f"posts_w2/{n+1:02d}_{it['key']}",
               tiktok=tt, instagram=ig, youtube_title=it['yt'], youtube_desc=ytd,
               youtube_pinned_comment=f"🎁 Free Christmas printables: {SHORT}", pin_title=it['pt'], pin_desc=it['pd'],
               pin_link=it['pin_link'], status="draft")
    assert len(it['yt']) <= 60, (it['key'], len(it['yt'])); assert len(it['pt']) < 100, it['pt']; assert len(it['pd']) < 500, (it['key'], len(it['pd']))
    assert len(tt) <= 2200 and len(ig) <= 2200
    cal.append(row)
for a, b in zip(cal, cal[1:]):
    assert a['hook_type'] != b['hook_type'], (a['key'], b['key'])
from collections import Counter
assert max(Counter(music).values()) <= 2, Counter(music)
json.dump(cal, open(f'{HERE}/calendar_w2.json', 'w'), indent=1, ensure_ascii=False)
print('calendar rows', len(cal))
