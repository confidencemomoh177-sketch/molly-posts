"""Coloring-transformation post: B&W page -> half colored -> fully colored -> cover CTA (+ pin, 15 s video).
Usage: python3 color_post.py item.json   (item: out, page_photo, colored, lines, tag, hook, sub, half_title, full_title, full_sub, + make_post keys for pin/slide 4)
"""
import sys, json, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_post as M
from PIL import Image, ImageDraw
W, H = M.W, M.H
r = {**M.DEFAULTS, **json.load(open(sys.argv[1]))}
out = r['out']; os.makedirs(out, exist_ok=True)
P, S, BG, A = map(M.rgb, (r['primary'], r['secondary'], r['background'], r['accent']))
col = Image.open(r['colored']).convert('RGB'); lin = Image.open(r['lines']).convert('RGB').resize(col.size)

# slides 4 + pin from the standard builder, using the colored page as the pin photo
r2 = dict(r, photo=r['colored'], page=r['page_photo'], layers=["x"], inside_title="x", page_title="x")
M.build(r2, out)

def framed(img, title, sub, name):
    s = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(s)
    d.rectangle((0, 0, W, 300), fill=S)
    for sz in (76, 68, 60):
        tf = M.font(M.SERIF, sz, 700); tl = M.wrap(d, title, tf, 960)
        if len(tl) == 1: break
    if len(tl) > 1: tf = M.font(M.SERIF, 62, 700); tl = M.wrap(d, title, tf, 960)
    M.centered(d, tl, tf, 150 - len(tl) * 37, "white")
    w = 860; im = img.resize((w, int(w * img.height / img.width)), Image.LANCZOS)
    card = M.shadowed(im, blur=18, off=12, alpha=110)
    s.paste(card, ((W - card.width) // 2, 330), card)
    if sub: M.centered(d, [sub], M.font(M.MED, 44), 330 + card.height + 5, S)
    s.save(f"{out}/{name}.png")

# Slide 2: half colored, Slide 3: fully colored (one diagonal sweep mask shared with the video)
def sweep_mask(size, t):
    w_, h_ = size; m = Image.new("L", size, 0); off = int((w_ + h_ * 0.5) * t)
    ImageDraw.Draw(m).polygon([(0, 0), (off, 0), (off - int(h_ * 0.5), h_), (0, h_)], fill=255); return m
HALF = 0.5
half = Image.composite(col, lin, sweep_mask(col.size, HALF))
framed(lin, r['hook'], r['sub'], "1_hook")
framed(half, r['half_title'], None, "2_half")
framed(col, r['full_title'], r.get('full_sub'), "3_full")
slides = [f"{out}/{n}.png" for n in ("1_hook", "2_half", "3_full", "4_book")]
for junk in ("2_layers.png", "3_page.png"):
    try: os.remove(f"{out}/{junk}")
    except FileNotFoundError: pass

# 15 s video, drawn frame by frame: B&W -> colour sweeps to halfway -> "Halfway there…" -> sweeps to full -> "All colored in!" -> cover
FPS = 30; total = 15.0
s1, s2, s3, s4 = (Image.open(x).convert("RGB") for x in slides)
w = 860; cw, ch = w, int(w * col.height / col.width)
colr = col.resize((cw, ch), Image.LANCZOS)
pad = 36; x0 = (W - cw - 2 * pad) // 2 + pad; y0 = 330 + pad
def sweep(base, t):
    f = base.copy(); f.paste(colr, (x0, y0), sweep_mask((cw, ch), t)); return f
ease = lambda u: 0.5 - 0.5 * __import__("math").cos(3.14159 * max(0, min(1, u)))
proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                         "-i", r['music'], "-filter_complex", f"[1:a]atrim=0:{total},afade=t=in:d=0.3,afade=t=out:st={total-1.5}:d=1.5,volume=0.9[a]",
                         "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20",
                         "-c:a", "aac", "-b:a", "160k", "-t", str(total), "-movflags", "+faststart", f"{out}/video.mp4"], stdin=subprocess.PIPE)
for n in range(int(total * FPS)):
    t = n / FPS
    if t < 2.4: fr = s1
    elif t < 4.4: fr = sweep(s1, HALF * ease((t - 2.4) / 2.0))
    elif t < 4.7: fr = Image.blend(sweep(s1, HALF), s2, (t - 4.4) / 0.3)
    elif t < 6.6: fr = s2
    elif t < 8.8: fr = sweep(s2, HALF + (1 - HALF) * ease((t - 6.6) / 2.2))
    elif t < 9.1: fr = Image.blend(sweep(s2, 1), s3, (t - 8.8) / 0.3)
    elif t < 11.6: fr = s3
    elif t < 12.2: fr = Image.blend(s3, s4, (t - 11.6) / 0.6)
    else: fr = s4
    proc.stdin.write(fr.tobytes())
proc.stdin.close(); proc.wait()
print("ok", out)
