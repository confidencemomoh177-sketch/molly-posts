"""Book Social Media Autopilot - build one post (4 slides + Pinterest pin + 15 s video) for one book item.

Usage:  python3 make_post.py book.json item.json
  book.json  = settings shared by every post for this book (cover, colours, wording)
  item.json  = one item (photo, page, hook, list lines ...). Item keys override book keys.
"""
import sys, json, subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

G = "/usr/share/fonts/truetype/google-fonts/"   # change if fonts live elsewhere
SERIF, BOLD, MED = G + "Lora-Variable.ttf", G + "Poppins-Bold.ttf", G + "Poppins-Medium.ttf"
W, H = 1080, 1920

DEFAULTS = {  # wording + colours; override any of these in book.json
    "primary": "#B22228", "secondary": "#1C4A30", "background": "#FCF6EB", "accent": "#FFDE96",
    "swipe_text": "swipe for the recipe",
    "inside_title": "What goes in the jar",
    "page_title": "Jar No. {num} from the book",
    "page_extra": "+ a printable gift tag for every jar",
    "more_title": "{more} more jars like this",
    "cta": "Link in bio",
    "pin_cta": "Get the recipe",
    "page_cut": 1470,      # px (at 200 dpi) where the book page is cut off on slide 3
    "page_side": 120,      # px trimmed off the page's left/right margins
}


def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight:
        try: f.set_variation_by_axes([weight])
        except Exception: pass
    return f


def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]


def centered(d, lines, f, y, fill, gap=1.2, stroke=0, w=W):
    for ln in lines:
        d.text(((w - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=fill,
               stroke_width=stroke, stroke_fill=(20, 10, 5))
        y += int(f.size * gap)
    return y


def pill(d, text, f, cx, y, bg, fg, px=40, py=18):
    tw = d.textlength(text, font=f)
    d.rounded_rectangle((cx - tw / 2 - px, y, cx + tw / 2 + px, y + f.size + 2 * py),
                        radius=(f.size + 2 * py) // 2, fill=bg)
    d.text((cx - tw / 2, y + py - f.size * .12), text, font=f, fill=fg)


def fill_frame(img, w, h):
    return ImageOps.fit(img, (w, h), Image.LANCZOS, centering=(0.5, 0.45))


def shadowed(img, blur=24, off=18, alpha=150):
    pad = blur * 2
    sh = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((pad, pad + off, pad + img.width, pad + img.height + off), fill=(0, 0, 0, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh.paste(img, (pad, pad))
    return sh


def gradient(img, top=0.15, bottom=0.85, start=0.30):
    g = Image.new("L", (1, img.height))
    for y in range(img.height):
        t = max(0, (y / img.height - start) / (1 - start))
        g.putpixel((0, y), int(255 * (top + (bottom - top) * t)))
    return Image.composite(Image.new("RGB", img.size, (15, 8, 5)), img, g.resize(img.size))


def build(r, out):
    os.makedirs(out, exist_ok=True)
    P, S, BG, A = rgb(r["primary"]), rgb(r["secondary"]), rgb(r["background"]), rgb(r["accent"])
    cover = Image.open(r["cover"]).convert("RGB")
    photo = Image.open(r["photo"]).convert("RGB")
    page = Image.open(r["page"]).convert("RGB")
    fmt = lambda s: s.format(num=r.get("num", ""), more=r.get("more", ""))

    # Slide 1 - hook over the item's real photo
    s1 = gradient(fill_frame(photo, W, H))
    d = ImageDraw.Draw(s1)
    # lay out bottom-up so the block always ends above the 400 px caption zone
    f = font(SERIF, 96, 700)
    lines = wrap(d, r["hook"], f, 940)
    block = len(lines) * int(96 * 1.2) + (25 + 58 if r.get("subhook") else 0)
    y0 = 1430 - block                      # bottom of the sub-line sits near y = 1430
    pill(d, r["tag"], font(BOLD, 40), W // 2, y0 - 100, P, "white")
    y = centered(d, lines, f, y0, "white", stroke=2)
    if r.get("subhook"):
        centered(d, [r["subhook"]], font(MED, 48), y + 25, A)
    centered(d, [r["swipe_text"]], font(MED, 40), 1470, (230, 230, 230))
    s1.save(f"{out}/1_hook.png")

    # Slide 2 - what's inside (3-5 numbered cards)
    s2 = ImageEnhance.Brightness(fill_frame(photo, W, H).filter(ImageFilter.GaussianBlur(20))).enhance(.42)
    d = ImageDraw.Draw(s2)
    tsz = 84
    while ImageDraw.Draw(s2).textlength(fmt(r["inside_title"]), font=font(SERIF, tsz, 700)) > 940: tsz -= 4
    centered(d, [fmt(r["inside_title"])], font(SERIF, tsz, 700), 300 + (84 - tsz) // 2, "white", stroke=2)
    y = 500
    for i, it in enumerate(r["layers"][:5], 1):
        d.rounded_rectangle((90, y, W - 90, y + 150), radius=30, fill=BG)
        d.ellipse((120, y + 25, 220, y + 125), fill=P)
        nf = font(BOLD, 54)
        d.text((170 - d.textlength(str(i), font=nf) / 2, y + 32), str(i), font=nf, fill="white")
        lf = font(MED, 46 if len(it) < 26 else 40 if len(it) < 30 else 34)
        d.text((255, y + 75 - lf.size * .62), it, font=lf, fill=S)
        y += 180
    if r.get("facts"):
        centered(d, [r["facts"]], font(MED, 42), y + 40, A)
    s2.save(f"{out}/2_layers.png")

    # Slide 3 - the real book page, cut off and faded so the book stays worth buying
    side = r["page_side"]
    crop = page.crop((side, r.get("page_top", 150), page.width - side, min(r["page_cut"], page.height)))
    fade = Image.new("L", crop.size, 255)
    fd = ImageDraw.Draw(fade)
    for i in range(160):
        fd.line((0, crop.height - 160 + i, crop.width, crop.height - 160 + i), fill=255 - int(i * 1.5))
    crop = Image.composite(crop, Image.new("RGB", crop.size, "white"), fade)
    crop = crop.resize((960, int(crop.height * 960 / crop.width)), Image.LANCZOS)
    s3 = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(s3)
    d.rectangle((0, 0, W, 330), fill=S)
    centered(d, [fmt(r["page_title"])], font(SERIF, 70, 700), 120, "white")
    card = shadowed(crop).rotate(-2, expand=True, resample=Image.BICUBIC)
    s3.paste(card, ((W - card.width) // 2, 380), card)
    if r.get("page_extra"):
        centered(d, [r["page_extra"]], font(MED, 44), 380 + card.height + 10, S)
    s3.save(f"{out}/3_page.png")

    # Slide 4 - the book + call to action
    s4 = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(s4)
    d.rectangle((0, 0, W, 300), fill=S)
    centered(d, [fmt(r["more_title"])], font(SERIF, 78, 700), 100, "white")
    cw = 780 if cover.height / cover.width < 1.45 else 700
    cw = min(cw, int(980 * cover.width / cover.height))   # keep cover + button clear of the bottom 400 px
    cv = cover.resize((cw, int(cw * cover.height / cover.width)), Image.LANCZOS)
    cc = shadowed(cv)
    s4.paste(cc, ((W - cc.width) // 2, 330), cc)
    pill(d, r["cta"], font(BOLD, 58), W // 2, 1395, P, "white", px=80, py=26)
    s4.save(f"{out}/4_book.png")

    # Pinterest pin 1000 x 1500
    PW, PH = 1000, 1500
    p = Image.new("RGB", (PW, PH), BG)
    p.paste(fill_frame(photo, PW, 980), (0, 0))
    d = ImageDraw.Draw(p)
    cv = cover.resize((300, int(300 * cover.height / cover.width)), Image.LANCZOS)
    cc = shadowed(cv, blur=14, off=10)
    p.paste(cc, (PW - cc.width - 10, 1010), cc)
    for psz in (66, 58, 52, 46):
        f = font(SERIF, psz, 700)
        tl = wrap(d, r["pin_title"], f, 560)
        if len(tl) <= 3: break
    y = 1015
    for ln in tl:
        d.text((50, y), ln, font=f, fill=P); y += int(psz * 1.18)
    sf = font(MED, 34)
    while d.textlength(r["pin_sub"], font=sf) > 590 and sf.size > 26: sf = font(MED, sf.size - 2)
    d.text((50, y + 10), r["pin_sub"], font=sf, fill=S)
    pill(d, r["pin_cta"], font(BOLD, 36), 200, 1390, P, "white")
    p.save(f"{out}/pin.png")
    return [f"{out}/{n}.png" for n in ("1_hook", "2_layers", "3_page", "4_book")]


def video(slides, music, out, per=3.6, xf=0.6):
    """15 s 9:16 video: slow zoom per slide, crossfades, music faded in/out. music=None -> silent track."""
    inputs, filt = [], []
    for i, s in enumerate(slides):
        inputs += ["-loop", "1", "-t", str(per + xf), "-i", s]
        frames = int((per + xf) * 30)
        filt.append(f"[{i}:v]scale=2160:3840,zoompan=z='min(1+0.0009*on,1.12)':d={frames}:"
                    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1,format=yuv420p[v{i}]")
    last = "v0"
    for i in range(1, len(slides)):
        filt.append(f"[{last}][v{i}]xfade=transition=fade:duration={xf}:offset={i * per:.2f}[x{i}]")
        last = f"x{i}"
    total, n = len(slides) * per + xf, len(slides)
    if music:
        inputs += ["-i", music]
    else:
        inputs += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    filt.append(f"[{n}:a]atrim=0:{total:.2f},afade=t=in:d=0.3,afade=t=out:st={total - 1.5:.2f}:d=1.5,volume=0.9[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", f"[{last}]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-preset", "veryfast", "-crf", "20",
                    "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    r = {**DEFAULTS, **json.load(open(sys.argv[1])), **json.load(open(sys.argv[2]))}
    slides = build(r, r["out"])
    if not r.get("no_video"):
        video(slides, r.get("music"), f"{r['out']}/video.mp4")
    print("ok", r["out"])
