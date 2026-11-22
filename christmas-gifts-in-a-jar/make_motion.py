"""Book Social Media Autopilot - 'moving photo' clip (no AI video credits needed).

Turns one still photo into a ~9 s vertical video:
  * 2.5D parallax: the jar/food is cut out (rembg) and moves at a different speed than the background
  * optional effects: rising steam, falling snow, twinkling lights
  * hook text on top for the first seconds, then a short caption, then the book end card

Usage: python3 make_motion.py book.json clip.json
clip.json: {"photo":..., "out":..., "tag":..., "hook":..., "caption":..., "end_card":"path/4_book.png",
            "music":..., "fx":[{"type":"steam","x":0.55,"y":0.55,"w":0.18}, {"type":"snow"}, {"type":"sparkle"}],
            "move":"in"|"left"|"right"}
"""
import sys, json, os, subprocess, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageOps
from make_post import DEFAULTS, SERIF, BOLD, MED, rgb, font, wrap, centered, pill

W, H, FPS = 1080, 1920, 30
CLIP, END, XF = 6.8, 2.4, 0.4          # seconds of motion, end card, crossfade


def ease(t):
    return t * t * (3 - 2 * t)


def cutout(img):
    from rembg import remove, new_session
    m = np.array(remove(Image.fromarray(img), session=new_session("u2net"), only_mask=True)).astype(np.float32) / 255
    m = cv2.GaussianBlur(m, (0, 0), 2)
    hard = (m > 0.5).astype(np.uint8) * 255
    bg = cv2.inpaint(img, cv2.dilate(hard, np.ones((25, 25), np.uint8)), 9, cv2.INPAINT_TELEA)
    return m, cv2.GaussianBlur(bg, (0, 0), 1.5)


def warp(a, scale, dx, dy, border=cv2.BORDER_REFLECT):
    M = np.float32([[scale, 0, (1 - scale) * W / 2 + dx], [0, scale, (1 - scale) * H / 2 + dy]])
    return cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=border)


class Steam:
    def __init__(s, x, y, w, n=36, seed=1):
        r = np.random.default_rng(seed)
        s.p = [dict(x0=(x + (r.random() - .5) * w) * W, y0=y * H, ph=r.random() * 6.28, t0=r.random(),
                    sp=0.18 + r.random() * 0.12, sw=15 + r.random() * 25) for _ in range(n)]

    def draw(s, layer, t):
        for p in s.p:
            u = (t * p["sp"] + p["t0"]) % 1
            yy = p["y0"] - u * 0.30 * H
            xx = p["x0"] + math.sin(p["ph"] + u * 6) * p["sw"]
            rad = int(18 + u * 70)
            a = math.sin(u * math.pi) * 0.34
            cv2.circle(layer, (int(xx), int(yy)), rad, a, -1)


class Snow:
    def __init__(s, n=170, seed=2):
        r = np.random.default_rng(seed)
        s.p = [dict(x=r.random() * W, y=r.random() * H, v=60 + r.random() * 140, rad=2 + r.random() * 5,
                    ph=r.random() * 6.28, a=0.5 + r.random() * 0.5) for _ in range(n)]

    def draw(s, layer, t):
        for p in s.p:
            yy = (p["y"] + p["v"] * t) % H
            xx = p["x"] + math.sin(p["ph"] + t * 1.5) * 18
            cv2.circle(layer, (int(xx), int(yy)), int(p["rad"]), p["a"], -1)


class Sparkle:
    def __init__(s, n=40, seed=3, top=0.45):
        r = np.random.default_rng(seed)
        s.p = [dict(x=r.random() * W, y=r.random() * H * top, f=1 + r.random() * 2, ph=r.random() * 6.28,
                    rad=3 + r.random() * 6) for _ in range(n)]

    def draw(s, layer, t):
        for p in s.p:
            a = max(0, math.sin(p["ph"] + t * p["f"] * 3)) ** 3 * 0.8
            cv2.circle(layer, (int(p["x"]), int(p["y"])), int(p["rad"]), a, -1)


def text_layers(r):
    P, A = rgb(r["primary"]), rgb(r["accent"])
    hook = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = Image.new("L", (1, H))
    for y in range(H):
        g.putpixel((0, y), int(230 * max(0.0, 1 - y / (H * 0.5)) ** 0.9))
    shade = Image.new("RGBA", (W, H), (12, 6, 4, 0)); shade.putalpha(g.resize((W, H)))
    hook.alpha_composite(shade)
    d = ImageDraw.Draw(hook)
    pill(d, r["tag"], font(BOLD, 40), W // 2, 230, P, "white")
    f = font(SERIF, 104, 700)
    y = centered(d, wrap(d, r["hook"], f, 860), f, 330, "white", stroke=3)
    if r.get("subhook"):
        centered(d, [r["subhook"]], font(MED, 50), y + 20, A, stroke=3)
    cap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(cap)
    cf = font(BOLD, 52)
    lines = wrap(d, r["caption"], cf, 900)
    bh = len(lines) * 66 + 50
    d.rounded_rectangle((60, 1380, W - 60, 1380 + bh), radius=36, fill=(255, 250, 240, 235))
    centered(d, lines, cf, 1405, rgb(r["secondary"]), gap=1.27)
    return np.array(hook).astype(np.float32) / 255, np.array(cap).astype(np.float32) / 255


def over(base, layer, k=1.0):
    a = layer[..., 3:4] * k
    return base * (1 - a) + layer[..., :3] * a


def build(r, out):
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    im = Image.open(r["photo"]).convert("RGB")
    im = np.array(ImageOps.fit(im, (W, H), Image.LANCZOS, centering=(r.get("crop_x", 0.5), r.get("crop_y", 0.5))))
    mask, bg = cutout(im)
    m3 = mask[..., None]
    fx = []
    for e in r.get("fx", []):
        if e["type"] == "steam": fx.append(Steam(e["x"], e["y"], e.get("w", 0.15)))
        if e["type"] == "snow": fx.append(Snow())
        if e["type"] == "sparkle": fx.append(Sparkle(top=e.get("top", 0.45)))
    hook, cap = text_layers(r)
    end = np.array(Image.open(r["end_card"]).convert("RGB").resize((W, H))).astype(np.float32) / 255
    mv = {"in": (0, 0, 0, 0), "left": (-40, 0, -70, 0), "right": (40, 0, 70, 0)}[r.get("move", "in")]
    n_clip, n_end = int(CLIP * FPS), int((END + XF) * FPS)
    tmp = out + ".silent.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
                          "-preset", "veryfast", "-crf", "20", tmp], stdin=subprocess.PIPE)
    last = None
    for i in range(n_clip):
        t = i / FPS; e = ease(i / (n_clip - 1))
        b = warp(bg, 1.04 + 0.03 * e, mv[0] * e, mv[1] * e).astype(np.float32) / 255
        fg = warp(im, 1.05 + 0.09 * e, mv[2] * e, 12 * e).astype(np.float32) / 255
        mk = warp(m3, 1.05 + 0.09 * e, mv[2] * e, 12 * e, cv2.BORDER_CONSTANT)[..., None]
        frame = b * (1 - mk) + fg * mk
        if fx:
            layer = np.zeros((H, W), np.float32)
            for f in fx: f.draw(layer, t)
            layer = cv2.GaussianBlur(layer, (0, 0), 6)[..., None]
            frame = frame * (1 - layer) + 1.0 * layer
        if t < 3.6:                                   # hook, fading out 3.2-3.6 s
            frame = over(frame, hook, 1.0 if t < 3.2 else (3.6 - t) / 0.4)
        elif t > 3.9:                                 # caption fades in
            frame = over(frame, cap, min(1.0, (t - 3.9) / 0.3))
        last = frame
        p.stdin.write((np.clip(frame, 0, 1) * 255).astype(np.uint8).tobytes())
    for i in range(n_end):                            # crossfade into the book end card
        k = min(1.0, i / (XF * FPS))
        frame = last * (1 - k) + end * k
        p.stdin.write((np.clip(frame, 0, 1) * 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    total = CLIP + END + XF
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", r["music"], "-filter_complex",
                    f"[1:a]atrim=0:{total:.2f},afade=t=out:st={total - 0.8:.2f}:d=0.8,volume=0.9[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}",
                    "-movflags", "+faststart", out], check=True)
    os.remove(tmp)
    # cover frame for checking / pins
    Image.fromarray((np.clip(over(warp(im, 1.05, 0, 0).astype(np.float32) / 255, hook), 0, 1) * 255).astype(np.uint8)).save(out.replace(".mp4", "_cover.jpg"), quality=92)


if __name__ == "__main__":
    r = {**DEFAULTS, **json.load(open(sys.argv[1])), **json.load(open(sys.argv[2]))}
    build(r, r["out"])
    print("ok", r["out"])
