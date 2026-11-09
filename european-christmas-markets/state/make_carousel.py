"""Build a 6-slide 1080x1350 swipe carousel: collage hook, 4 item slides, book CTA.
Usage: python3 make_carousel.py <img_dir> <cover> <out_root>   (reads carousels_w2.CAROUSELS)"""
import sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_post import font, wrap, centered, pill, shadowed, gradient, rgb, SERIF, BOLD, MED
from carousels_w2 import CAROUSELS

W, H = 1080, 1350
P, S, BG, A = rgb("#B3202A"), rgb("#14295A"), rgb("#FCF6EB"), rgb("#F4C76A")
IMG, COVER, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
cover = Image.open(COVER).convert("RGB")

def photo(n, w, h):
    return ImageOps.fit(Image.open(f"{IMG}/i-{n:03d}.png").convert("RGB"), (w, h), Image.LANCZOS, centering=(0.5, 0.45))

def fit_font(d, text, path, size, maxw, weight=None, minsize=30):
    while size > minsize and d.textlength(text, font=font(path, size, weight)) > maxw: size -= 2
    return font(path, size, weight)

def build(c):
    out = f"{OUT}/{c['key']}"; os.makedirs(out, exist_ok=True); files = []
    # 1 - collage + hook
    s = Image.new("RGB", (W, H))
    for i, (n, *_ ) in enumerate(c["items"]):
        s.paste(photo(n, W // 2, H // 2), ((i % 2) * W // 2, (i // 2) * H // 2))
    s = gradient(s, top=0.25, bottom=0.92, start=0.25)
    d = ImageDraw.Draw(s)
    f = font(SERIF, 92, 700); lines = wrap(d, c["hook"], f, 940)
    y0 = 1130 - len(lines) * 110
    pill(d, c["tag"], font(BOLD, 38), W // 2, y0 - 95, P, "white")
    y = centered(d, lines, f, y0, "white", stroke=2)
    centered(d, ["swipe to see all 4"], font(MED, 42), y + 30, A)
    files.append(s)
    # 2-5 - one item per slide
    for i, (n, name, l1, l2) in enumerate(c["items"], 1):
        s = Image.new("RGB", (W, H), BG)
        s.paste(photo(n, W, 860), (0, 0))
        d = ImageDraw.Draw(s)
        d.ellipse((60, 780, 200, 920), fill=P, outline=BG, width=8)
        nf = font(BOLD, 72); d.text((130 - d.textlength(str(i), font=nf) / 2, 797), str(i), font=nf, fill="white")
        nfnt = fit_font(d, name, SERIF, 70, 940, 700)
        d.text((70, 950), name, font=nfnt, fill=P)
        d.text((70, 1060), l1, font=fit_font(d, l1, BOLD, 46, 940), fill=S)
        d.text((70, 1130), l2, font=fit_font(d, l2, MED, 40, 940), fill=S)
        d.text((W - 70 - d.textlength(f"{i}/4", font=font(MED, 34)), 1250), f"{i}/4", font=font(MED, 34), fill=(150, 150, 150))
        files.append(s)
    # 6 - the book
    s = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(s)
    d.rectangle((0, 0, W, 230), fill=S)
    centered(d, ["Dates & hours for every market"], fit_font(d, "Dates & hours for every market", SERIF, 64, 980, 700), 80, "white")
    ch = 820; cv = cover.resize((int(ch * cover.width / cover.height), ch), Image.LANCZOS)
    cc = shadowed(cv); s.paste(cc, ((W - cc.width) // 2, 230), cc)
    pill(d, "Link in bio", font(BOLD, 56), W // 2, 1150, P, "white", px=80, py=24)
    files.append(s)
    paths = []
    for k, im in enumerate(files, 1):
        p = f"{out}/{k}.jpg"; im.save(p, quality=90); paths.append(p)
    return paths

if __name__ == "__main__":
    for c in CAROUSELS: print(c["key"], len(build(c)))
