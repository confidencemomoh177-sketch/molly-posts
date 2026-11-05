"""Swap the 'Free coloring page of the week' on the website.
Usage: python3 rotate_free_page.py <page_num_1_to_50> "<Short title>"
Uses the coloring book PDF at /home/claude/cozy/coloring.pdf (restored by setup.sh), reads the page's
story line as the caption, writes ../site/free/free-coloring-page-of-the-week.pdf and the preview image,
records it in free_pages.json (with a history list). Then run build_site.py.
Never reuse a page that is in free_pages.json (sample, weekly or history)."""
import sys, json, os, subprocess, datetime
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, '..', 'site')
num, title = int(sys.argv[1]), sys.argv[2]
data = json.load(open(os.path.join(HERE, 'free_pages.json')))
used = {data['sample']['num'], data['weekly']['num']} | {h['num'] for h in data.get('history', [])}
if num in used:
    sys.exit(f'page {num} was already given away; pick another')
pdfp = 2 * num + 7
txt = subprocess.run(['pdftotext', '-f', str(pdfp), '-l', str(pdfp), '-layout', '/home/claude/cozy/coloring.pdf', '-'],
                     capture_output=True, text=True).stdout
lines = [l.strip() for l in txt.splitlines() if l.strip() and 'Coloring page' not in l]
caption = lines[0] if lines else title
tmp = '/tmp/free_week'
subprocess.run(['pdftoppm', '-r', '300', '-f', str(pdfp), '-l', str(pdfp), '-png', '-singlefile',
                '/home/claude/cozy/coloring.pdf', tmp], check=True)
im = Image.open(tmp + '.png').convert('RGB')
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 30)
t = 'Free page of the week · Cozy Christmas Coloring Book · wonderkidzstudio.netlify.app'
w = d.textlength(t, font=f)
d.rectangle(((im.width - w) / 2 - 20, im.height - 95, (im.width + w) / 2 + 20, im.height - 45), fill='white')
d.text(((im.width - w) / 2, im.height - 92), t, font=f, fill='#555555')
im.save(os.path.join(SITE, 'free', 'free-coloring-page-of-the-week.pdf'), resolution=300)
th = im.copy(); th.thumbnail((600, 780))
th.save(os.path.join(SITE, 'img', 'free-coloring-page-of-the-week.jpg'), quality=82, optimize=True)
data.setdefault('history', []).append({k: data['weekly'][k] for k in ('num', 'title', 'week_of')})
data['weekly'] = {"title": title, "caption": caption, "num": num, "week_of": datetime.date.today().isoformat(),
                  "pdf": "free/free-coloring-page-of-the-week.pdf", "img": "img/free-coloring-page-of-the-week.jpg"}
json.dump(data, open(os.path.join(HERE, 'free_pages.json'), 'w'), indent=1, ensure_ascii=False)
print('weekly free page ->', num, title, '|', caption)
