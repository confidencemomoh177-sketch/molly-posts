"""Book Social Media Autopilot v2 - short, stronger format.

Changes from v1 (based on week-1 TikTok data: viewers left after 1-3 s of 15 s):
  * Slide 1: hook text at the TOP in large type over the product photo, so the
    promise and the jar are both visible in the first second.
  * Video: about 8.5 s (2.5 + 2 + 2 + 2), quick 0.25 s cuts, stronger zoom.
  * New "list" post type: 3-5 jars from the book on one theme, with the book's own
    gift-guide page as proof.

Usage:  python3 make_post2.py book.json item.json        (item with "type": "recipe" or "list")
"""
import sys, json, subprocess, os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
from make_post import (DEFAULTS, W, H, SERIF, BOLD, MED, rgb, font, wrap, centered, pill,
                       fill_frame, shadowed, build as build_v1)


def top_gradient(img, strength=0.9, end=0.62):
    """Darken the top of the image (where the hook sits), fading to clear by `end`."""
    g = Image.new("L", (1, img.height))
    for y in range(img.height):
        t = max(0.0, 1 - (y / img.height) / end)
        g.putpixel((0, y), int(255 * strength * t ** 0.8))
    return Image.composite(Image.new("RGB", img.size, (12, 6, 4)), img, g.resize(img.size))


def hook_top(base_img, r, P, A, out):
    s1 = top_gradient(base_img)
    d = ImageDraw.Draw(s1)
    pill(d, r["tag"], font(BOLD, 40), W // 2, 230, P, "white")
    f = font(SERIF, 104, 700)
    y = centered(d, wrap(d, r["hook"], f, 860), f, 330, "white", stroke=3)
    if r.get("subhook"):
        centered(d, [r["subhook"]], font(MED, 50), y + 20, A, stroke=3)
    s1.save(f"{out}/1_hook.png")


def collage(paths, w, h, gap=8):
    imgs = [Image.open(p).convert("RGB") for p in paths[:4]]
    c = Image.new("RGB", (w, h), (20, 12, 8))
    if len(imgs) == 3:
        top = fill_frame(imgs[0], w, h // 2 - gap // 2)
        c.paste(top, (0, 0))
        for i, im in enumerate(imgs[1:]):
            c.paste(fill_frame(im, w // 2 - gap // 2, h // 2 - gap // 2), (i * (w // 2 + gap // 2), h // 2 + gap // 2))
    else:
        cw, ch = w // 2 - gap // 2, h // 2 - gap // 2
        for i, im in enumerate(imgs):
            c.paste(fill_frame(im, cw, ch), ((i % 2) * (cw + gap), (i // 2) * (ch + gap)))
    return c


def page_crop(r, page, width=960):
    side = r.get("page_side", 120)
    crop = page.crop((side, r.get("page_top", 150), page.width - side, min(r["page_cut"], page.height)))
    fade = Image.new("L", crop.size, 255)
    fd = ImageDraw.Draw(fade)
    k = r.get("page_fade", 120)
    for i in range(k):
        fd.line((0, crop.height - k + i, crop.width, crop.height - k + i), fill=255 - int(i * 240 / k))
    crop = Image.composite(crop, Image.new("RGB", crop.size, "white"), fade)
    return crop.resize((width, int(crop.height * width / crop.width)), Image.LANCZOS)


def build_list(r, out):
    os.makedirs(out, exist_ok=True)
    P, S, BG, A = rgb(r["primary"]), rgb(r["secondary"]), rgb(r["background"]), rgb(r["accent"])
    cover = Image.open(r["cover"]).convert("RGB")
    items = r["items"]
    photos = [it["photo"] for it in items]

    # 1 hook over a collage
    hook_top(collage(photos, W, H), r, P, A, out)

    # 2 the list with thumbnails
    s2 = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(s2)
    d.rectangle((0, 0, W, 300), fill=S)
    centered(d, [r["list_title"]], font(SERIF, 70, 700), 120, "white")
    n = len(items)
    row = min(330, (1640 - 360) // n)
    y = 360 + ((1640 - 360) - row * n) // 2
    for i, it in enumerate(items, 1):
        th = fill_frame(Image.open(it["photo"]).convert("RGB"), row - 30, row - 30)
        s2.paste(th, (70, y))
        d.ellipse((46, y - 24, 118, y + 48), fill=P)
        d.text((82 - d.textlength(str(i), font=font(BOLD, 42)) / 2, y - 22), str(i), font=font(BOLD, 42), fill="white")
        x = 70 + row - 30 + 30
        big = row >= 300
        nf = font(BOLD, (54 if big else 46) if len(it["name"]) < 20 else (46 if big else 40))
        ff = font(MED, 40 if big else 34)
        ty = y + (row - 30 - nf.size - 14 - ff.size) // 2 - 6
        d.text((x, ty), it["name"], font=nf, fill=S)
        d.text((x, ty + nf.size + 14), it["fact"], font=ff, fill=(110, 90, 80))
        y += row
    s2.save(f"{out}/2_layers.png")

    # 3 the book's own guide page
    page = Image.open(r["page"]).convert("RGB")
    crop = page_crop(r, page, 1000)
    s3 = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(s3)
    d.rectangle((0, 0, W, 330), fill=S)
    centered(d, [r["page_title"]], font(SERIF, 66, 700), 125, "white")
    card = shadowed(crop).rotate(-2, expand=True, resample=Image.BICUBIC)
    nf = font(SERIF, 60, 700)
    note = r.get("page_note", "The book sorts all 100 jars by person, budget and time")
    lines = wrap(d, note, nf, 900)
    block = card.height + 40 + len(lines) * 72
    cy = 330 + (1560 - 330 - block) // 2
    s3.paste(card, ((W - card.width) // 2, cy), card)
    centered(d, lines, nf, cy + card.height + 40, S)
    s3.save(f"{out}/3_page.png")

    # 4 the book
    s4 = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(s4)
    d.rectangle((0, 0, W, 300), fill=S)
    centered(d, [r["more_title"]], font(SERIF, 72, 700), 105, "white")
    cv = cover.resize((780, int(780 * cover.height / cover.width)), Image.LANCZOS)
    cc = shadowed(cv)
    s4.paste(cc, ((W - cc.width) // 2, 330), cc)
    pill(d, r["cta"], font(BOLD, 58), W // 2, 1500, P, "white", px=80, py=26)
    s4.save(f"{out}/4_book.png")

    # pin
    PW, PH = 1000, 1500
    p = Image.new("RGB", (PW, PH), BG)
    p.paste(collage(photos, PW, 980), (0, 0))
    d = ImageDraw.Draw(p)
    cv = cover.resize((300, int(300 * cover.height / cover.width)), Image.LANCZOS)
    cc = shadowed(cv, blur=14, off=10)
    p.paste(cc, (PW - cc.width - 10, 1010), cc)
    f = font(SERIF, 62, 700)
    y = 1015
    for ln in wrap(d, r["pin_title"], f, 560):
        d.text((50, y), ln, font=f, fill=P); y += 74
    d.text((50, y + 10), r["pin_sub"], font=font(MED, 34), fill=S)
    pill(d, r["pin_cta"], font(BOLD, 36), 210, 1390, P, "white")
    p.save(f"{out}/pin.png")
    return [f"{out}/{x}.png" for x in ("1_hook", "2_layers", "3_page", "4_book")]


def build_recipe(r, out):
    slides = build_v1(r, out)                     # slides 2-4 and pin from v1
    P, A = rgb(r["primary"]), rgb(r["accent"])
    hook_top(fill_frame(Image.open(r["photo"]).convert("RGB"), W, H), r, P, A, out)   # new slide 1
    return slides


def video_short(slides, music, out, per=(2.5, 2.0, 2.0, 2.2), xf=0.25):
    inputs, filt = [], []
    for i, s in enumerate(slides):
        dur = per[i] + xf
        inputs += ["-loop", "1", "-t", f"{dur:.2f}", "-i", s]
        frames = int(dur * 30)
        z = "min(1+0.0025*on,1.06)" if i == 0 else "min(1+0.0015*on,1.05)"
        filt.append(f"[{i}:v]scale=2160:3840,zoompan=z='{z}':d={frames}:"
                    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1,format=yuv420p[v{i}]")
    last, t = "v0", 0.0
    for i in range(1, len(slides)):
        t += per[i - 1]
        filt.append(f"[{last}][v{i}]xfade=transition=slideleft:duration={xf}:offset={t:.2f}[x{i}]")
        last = f"x{i}"
    total = sum(per) + xf
    n = len(slides)
    inputs += ["-i", music] if music else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    filt.append(f"[{n}:a]atrim=0:{total:.2f},afade=t=out:st={total - 0.8:.2f}:d=0.8,volume=0.9[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", f"[{last}]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
                    "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}",
                    "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    r = {**DEFAULTS, **json.load(open(sys.argv[1])), **json.load(open(sys.argv[2]))}
    slides = build_list(r, r["out"]) if r.get("type") == "list" else build_recipe(r, r["out"])
    video_short(slides, r.get("music"), f"{r['out']}/video.mp4")
    print("ok", r["out"])
