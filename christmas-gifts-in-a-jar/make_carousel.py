"""Book Social Media Autopilot - swipeable carousel (Instagram carousel + TikTok photo post).

Slides are 1080 x 1350 (4:5) JPGs: one cover, N tip slides, one book slide.
Usage:  python3 make_carousel.py book.json carousel.json
carousel.json: {"out":..., "tag":..., "hook":..., "subhook":..., "cover_photo":...,
                "slides":[{"photo":..., "title":..., "body":..., "focus":0.5}, ...],
                "cta_title":..., "cta_sub":...}
"""
import sys, json, os
from PIL import Image, ImageDraw, ImageOps
from make_post import DEFAULTS, SERIF, BOLD, MED, rgb, font, wrap, centered, pill, shadowed

CW, CH = 1080, 1350


def fit(img, w, h, fx=0.5, fy=0.5):
    return ImageOps.fit(img.convert("RGB"), (w, h), Image.LANCZOS, centering=(fx, fy))


def top_shade(img, strength=0.88, end=0.6):
    g = Image.new("L", (1, img.height))
    for y in range(img.height):
        t = max(0.0, 1 - (y / img.height) / end)
        g.putpixel((0, y), int(255 * strength * t ** 0.85))
    return Image.composite(Image.new("RGB", img.size, (12, 6, 4)), img, g.resize(img.size))


def counter(d, i, n, fill):
    t = f"{i}/{n}"
    f = font(BOLD, 30)
    w = d.textlength(t, font=f)
    d.rounded_rectangle((CW - w - 80, 40, CW - 40, 92), radius=26, fill=(0, 0, 0, 0) if fill is None else fill)
    d.text((CW - w - 60, 47), t, font=f, fill="white")


def build(r, out):
    os.makedirs(out, exist_ok=True)
    P, S, BG, A = rgb(r["primary"]), rgb(r["secondary"]), rgb(r["background"]), rgb(r["accent"])
    n = len(r["slides"]) + 2
    paths = []

    # 1 cover
    c = top_shade(fit(Image.open(r["cover_photo"]), CW, CH, 0.5, r.get("cover_focus", 0.55)))
    d = ImageDraw.Draw(c)
    pill(d, r["tag"], font(BOLD, 38), CW // 2, 150, P, "white")
    f = font(SERIF, 98, 700)
    y = centered(d, wrap(d, r["hook"], f, 900), f, 250, "white", stroke=3, w=CW)
    if r.get("subhook"):
        y = centered(d, [r["subhook"]], font(MED, 46), y + 14, A, stroke=3, w=CW)
    pill(d, "swipe", font(BOLD, 36), CW // 2, CH - 130, (255, 255, 255), S, px=46, py=14)
    counter(d, 1, n, (0, 0, 0))
    paths.append(f"{out}/01.jpg"); c.save(paths[-1], quality=92)

    # tip slides
    for i, s in enumerate(r["slides"], 2):
        im = Image.new("RGB", (CW, CH), BG)
        ph = fit(Image.open(s["photo"]), CW, 640, s.get("fx", 0.5), s.get("focus", 0.5))
        im.paste(ph, (0, 0))
        d = ImageDraw.Draw(im)
        counter(d, i, n, (0, 0, 0))
        d.ellipse((70, 590, 170, 690), fill=P)
        num = str(s.get("num", i - 1))
        nf = font(BOLD, 54)
        d.text((120 - d.textlength(num, font=nf) / 2, 604), num, font=nf, fill="white")
        tf = font(SERIF, 70, 700)
        y = 725
        for ln in wrap(d, s["title"], tf, 940):
            d.text((70, y), ln, font=tf, fill=S); y += 84
        y += 16
        bf = font(MED, 41)
        for para in s["body"].split("\n"):
            for ln in wrap(d, para, bf, 940):
                d.text((70, y), ln, font=bf, fill=(70, 55, 48)); y += 56
            y += 16
        assert y < CH - 75, (out, s["title"], y)
        d.text((70, CH - 70), r.get("footer", "From the book: Christmas Gifts in a Jar"), font=font(MED, 28), fill=(150, 130, 120))
        paths.append(f"{out}/{i:02d}.jpg"); im.save(paths[-1], quality=92)

    # book slide
    b = Image.new("RGB", (CW, CH), BG)
    d = ImageDraw.Draw(b)
    d.rectangle((0, 0, CW, 250), fill=S)
    tf = font(SERIF, 64, 700)
    lines = wrap(d, r["cta_title"], tf, 940)
    centered(d, lines, tf, 125 - len(lines) * 39, "white", w=CW)
    cover = Image.open(r["cover"]).convert("RGB")
    cv = cover.resize((int(820 * cover.width / cover.height), 820), Image.LANCZOS)
    cc = shadowed(cv)
    b.paste(cc, ((CW - cc.width) // 2, 270), cc)
    centered(d, [r.get("cta_sub", "100 jars + printable gift tags")], font(MED, 40), 1150, S, w=CW)
    pill(d, r.get("cta", "Link in bio"), font(BOLD, 52), CW // 2, 1215, P, "white", px=70, py=22)
    paths.append(f"{out}/{n:02d}.jpg"); b.save(paths[-1], quality=92)
    return paths


if __name__ == "__main__":
    r = {**DEFAULTS, **json.load(open(sys.argv[1])), **json.load(open(sys.argv[2]))}
    print(len(build(r, r["out"])), "slides ->", r["out"])
