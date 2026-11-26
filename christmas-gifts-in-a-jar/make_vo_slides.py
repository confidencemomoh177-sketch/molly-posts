"""Voiceover version of a slideshow post (recipe or list): each slide stays up while its line is spoken.
Usage: python3 make_vo_slides.py book.json vo.json
vo.json: {"out":..., "slides":[path1..path4], "script":[[lines for slide 1], [lines for slide 2], ...],
          "music":..., "voice":"af_heart", "speed":1.08, "music_vol":0.10}
"""
import sys, json, os, subprocess
import numpy as np, soundfile as sf
from PIL import Image
from make_post import DEFAULTS
from make_vo import voice_lines, timeline, mix, SR

W, H, FPS, XF = 1080, 1920, 30, 0.25


def build(r, out):
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    groups = r["script"]
    flat = [ln for g in groups for ln in g]
    clips = voice_lines(flat, r.get("voice", "af_heart"), r.get("speed", 1.08))
    starts, total, vo = timeline(clips)
    vo_path = out + ".vo.wav"; sf.write(vo_path, vo, SR)
    # slide i starts with its first line (slide 1 at 0)
    idx, bounds = 0, []
    for g in groups:
        bounds.append(starts[idx]); idx += len(g)
    bounds[0] = 0.0
    bounds.append(total)
    big = [np.array(Image.open(p).convert("RGB").resize((W * 2, H * 2), Image.LANCZOS)) for p in r["slides"]]
    tmp = out + ".silent.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
                          "-preset", "veryfast", "-crf", "20", tmp], stdin=subprocess.PIPE)

    def frame(k, t):                       # slow zoom on slide k
        a, b = bounds[k], bounds[k + 1]
        z = 1 + (0.07 if k == 0 else 0.045) * min(1, (t - a) / max(0.1, b - a))
        img = big[k]; h, w = img.shape[:2]
        cw, ch = int(w / z), int(h / z)
        x0, y0 = (w - cw) // 2, (h - ch) // 2
        return np.array(Image.fromarray(img[y0:y0 + ch, x0:x0 + cw]).resize((W, H), Image.BILINEAR)).astype(np.float32)

    for i in range(int(total * FPS)):
        t = i / FPS
        k = max(j for j in range(len(groups)) if bounds[j] <= t)
        f = frame(k, t)
        if k > 0 and t - bounds[k] < XF:   # slide-in from the right
            u = (t - bounds[k]) / XF; u = u * u * (3 - 2 * u)
            prev = frame(k - 1, t); off = int(W * (1 - u))
            f = np.concatenate([prev[:, W - off:] if off else prev[:, :0], f[:, :W - off]], axis=1) if off else f
        p.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    mix(tmp, vo_path, r["music"], total, r.get("music_vol", 0.10), out)
    os.remove(tmp); os.remove(vo_path)
    return total


if __name__ == "__main__":
    r = {**DEFAULTS, **json.load(open(sys.argv[1])), **json.load(open(sys.argv[2]))}
    print("ok", r["out"], round(build(r, r["out"]), 1), "s")
