"""Full-wrap paperback cover for B&N Press: back | spine | front, 8.5x11 trim, 0.125" bleed, 300 dpi.
Usage: python3 cover.py <pages> [inches_per_page]"""
import sys, io, qrcode
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

PAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 60
PER = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0025
DPI, TW, TH, BL = 300, 8.5, 11, 0.125
SP = PAGES * PER
W, H = round((2 * TW + SP + 2 * BL) * DPI), round((TH + 2 * BL) * DPI)
px = lambda inch: round(inch * DPI)
G = "/usr/share/fonts/truetype/google-fonts/"
F = lambda n, s: ImageFont.truetype(G + n, s)
NAVY, NAVY2, CREAM, RED, GOLD, GREEN, INK = "#13325e", "#0c2140", "#FCF6EB", "#C62033", "#FFD257", "#1C4A33", "#1F2433"

c = Image.new("RGB", (W, H), NAVY)
# night-sky gradient + snow on back and spine
grad = Image.new("L", (1, H))
for y in range(H): grad.putpixel((0, y), int(255 * y / H))
c.paste(Image.new("RGB", (W, H), NAVY2), (0, 0), grad.resize((W, H)))
d = ImageDraw.Draw(c)
random.seed(7)
back_w = px(BL + TW)
for _ in range(380):
    x, y, r = random.randint(0, back_w + px(SP)), random.randint(0, H), random.choice([2, 2, 3, 3, 4])
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, ))

# front cover (upscaled art), scaled to cover the front panel incl. bleed
import os
front = Image.open(os.environ.get("FRONT", "front_x3.png")).convert("RGB")
fw, fh = px(TW + BL), px(TH + 2 * BL)
s = max(fw / front.width, fh / front.height)
front = front.resize((round(front.width * s), round(front.height * s)), Image.LANCZOS)
ox, oy = (front.width - fw) // 2, (front.height - fh) // 2
c.paste(front.crop((ox, oy, ox + fw, oy + fh)), (W - fw, 0))

# ---- back cover (safe area: 0.375" from trim) ----
L, R = px(BL + 0.5), px(BL + TW - 0.5)
cw = R - L
def center(text, font, y, fill, maxw=cw, lh=1.25):
    words, line, out = text.split(), "", []
    for w_ in words:
        t = (line + " " + w_).strip()
        if d.textlength(t, font=font) <= maxw: line = t
        else: out.append(line); line = w_
    out.append(line)
    for ln in out:
        d.text((L + (cw - d.textlength(ln, font=font)) / 2, y), ln, font=font, fill=fill); y += int(font.size * lh)
    return y

y = px(BL + 0.5)
y = center("Find a golden star every day until Christmas!", F("Lora-Variable.ttf", 128), y, GOLD, lh=1.12) + 40
y = center("On the first day of December, Grandma Owl gives Pip, Juniper and Waddles a little glass lantern. "
           "Every day until Christmas, one golden star appears somewhere in Snuggle Woods. "
           "Can your child help them find all 25 stars?", F("Poppins-Regular.ttf", 54), y, "white", lh=1.42) + 50

# feature panel
items = ["25 short read-aloud stories, one for each day until Christmas",
         "25 pictures to color, with a golden star to spot",
         "25 activities: crafts, games and puzzles",
         "25 kindness missions to share with family and friends",
         "Star tracker, paper chain strips, answer key and a certificate"]
fi = F("Poppins-Medium.ttf", 50)
ph = 80 + len(items) * 92
d.rounded_rectangle((L, y, R, y + ph), 40, fill=CREAM)
yy = y + 38
for it in items:
    d.text((L + 50, yy - 4), "★", font=F("Poppins-Bold.ttf", 44), fill=RED) if False else None
    d.ellipse((L + 52, yy + 18, L + 80, yy + 46), fill=RED)
    d.text((L + 100, yy), it, font=fi, fill=INK); yy += 92
y += ph + 60

# sample pages
doc = fitz.open("out/Cozy_Christmas_Countdown_Interior.pdf")
thumbs = []
for p in [7, 24, 6]:  # Day 1 story, Day 4 story, word search
    pix = doc[p - 1].get_pixmap(dpi=110)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    im.thumbnail((px(2.3), px(2.98)), Image.LANCZOS); thumbs.append(im)
gap = (cw - sum(t.width for t in thumbs)) // 2
x = L
for t in thumbs:
    sh = Image.new("RGBA", (t.width + 40, t.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((20, 26, 20 + t.width, 26 + t.height), fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(10)); c.paste(sh, (x - 20, y - 20), sh)
    c.paste(t, (x, y)); d.rectangle((x, y, x + t.width, y + t.height), outline="white", width=6)
    x += t.width + gap
y += thumbs[0].height + 60
center("For ages 4–8 · One cozy day at a time from December 1st to 25th", F("Poppins-Bold.ttf", 48), y, GOLD)

# bottom: QR + site on the left, barcode space on the right
q = qrcode.QRCode(border=2, box_size=20); q.add_data("https://wonderkidzstudio.pages.dev/"); q.make(fit=True)
qi = q.make_image(fill_color="black", back_color="white").convert("RGB").resize((px(0.95), px(0.95)), Image.NEAREST)
by = H - px(BL + 0.45) - px(1.2)
c.paste(qi, (L, by + px(0.25)))
d.text((L + px(1.1), by + px(0.35)), "More books & free printables:", font=F("Poppins-Regular.ttf", 36), fill="white")
d.text((L + px(1.1), by + px(0.55)), "wonderkidzstudio.pages.dev", font=F("Poppins-Bold.ttf", 44), fill=GOLD)
d.text((L + px(1.1), by + px(0.82)), "Wonder Kidz Studio", font=F("Lora-Variable.ttf", 42), fill="white")
d.rectangle((R - px(2.0), by, R, by + px(1.2)), fill="white")  # barcode area (2 x 1.2 in)

# spine: no text under 48... B&N allows text from 48 pages, but a sub-0.25" spine is too thin to read; keep it plain
sx = px(BL + TW)
d.rectangle((sx, 0, sx + px(SP), H), fill=RED)

c.save("out/Cozy_Christmas_Countdown_Cover.png")
Image.open("out/Cozy_Christmas_Countdown_Cover.png").save("out/Cozy_Christmas_Countdown_Cover.pdf", "PDF", resolution=DPI)
print(f"{W}x{H}px = {W/DPI:.3f} x {H/DPI:.3f} in, spine {SP:.3f} in ({PAGES} pages x {PER})")
