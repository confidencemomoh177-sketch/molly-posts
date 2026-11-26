"""Book Social Media Autopilot - voiceover video (moving photo + American voice + soft music).

The script is a list of short spoken lines. Each line is voiced with Kokoro (American English),
and shown on screen while it is spoken:
  line 1  -> big hook at the top
  middle  -> caption box near the bottom, one line at a time
  last    -> the book end card (the call to action)
Music sits underneath at low volume and dips further while the voice speaks.

Usage: python3 make_vo.py book.json clip.json
clip.json: like make_motion.py plus "script": [line1, line2, ...], optional "voice" (default af_heart),
           "speed" (default 1.0), "music_vol" (default 0.10)
"""
import sys, json, os, subprocess
import numpy as np, cv2, soundfile as sf
from PIL import Image, ImageDraw, ImageOps
from make_post import DEFAULTS, BOLD, rgb, font, wrap, centered
from make_motion import W, H, FPS, XF, ease, cutout, warp, Steam, Snow, Sparkle, text_layers, over

TTS_DIR = "/home/claude/tts"
GAP = 0.28          # pause between lines
TAIL = 1.2          # seconds of end card after the last word
SR = 24000


def voice_lines(lines, voice, speed):
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{TTS_DIR}/kokoro-v1.0.onnx", f"{TTS_DIR}/voices-v1.0.bin")
    out = []
    for ln in lines:
        s, sr = k.create(ln, voice=voice, speed=speed, lang="en-us")
        assert sr == SR
        out.append(np.asarray(s, np.float32))
    return out


def cap_layer(text, r):
    cap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(cap)
    cf = font(BOLD, 56)
    lines = wrap(d, text, cf, 900)
    bh = len(lines) * 70 + 50
    y0 = 1360
    d.rounded_rectangle((60, y0, W - 60, y0 + bh), radius=36, fill=(255, 250, 240, 238))
    centered(d, lines, cf, y0 + 25, rgb(r["secondary"]), gap=1.25)
    return np.array(cap).astype(np.float32) / 255


def mix(tmp, vo_path, music, total, mv_, out):
    """voice on top, music low and ducked under the voice"""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", vo_path, "-stream_loop", "-1", "-i", music,
                    "-filter_complex",
                    f"[1:a]aresample=44100,volume=1.6,asplit=2[v][sc];"
                    f"[2:a]aresample=44100,atrim=0:{total:.2f},volume={mv_},"
                    f"afade=t=in:d=0.6,afade=t=out:st={total - 1.0:.2f}:d=1.0[m];"
                    f"[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=400[md];"
                    f"[v][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}",
                    "-movflags", "+faststart", out], check=True)


def timeline(clips, start=0.35):
    starts, t = [], start
    for c in clips:
        starts.append(t); t += len(c) / SR + GAP
    total = starts[-1] + len(clips[-1]) / SR + TAIL
    vo = np.zeros(int(total * SR) + SR, np.float32)
    for s0, c in zip(starts, clips):
        i = int(s0 * SR); vo[i:i + len(c)] += c
    return starts, total, vo[:int(total * SR)]


def build(r, out):
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    lines = r["script"]
    clips = voice_lines(lines, r.get("voice", "af_heart"), r.get("speed", 1.0))
    # timeline: start time of each line
    starts, t = [], 0.35
    for c in clips:
        starts.append(t); t += len(c) / SR + GAP
    total = starts[-1] + len(clips[-1]) / SR + TAIL
    t_end = starts[-1] - 0.15                       # end card fades in just before the last line
    # voice track
    vo = np.zeros(int(total * SR) + SR, np.float32)
    for s0, c in zip(starts, clips):
        i = int(s0 * SR); vo[i:i + len(c)] += c
    vo = vo[:int(total * SR)]
    vo_path = out + ".vo.wav"; sf.write(vo_path, vo, SR)

    # picture
    im = Image.open(r["photo"]).convert("RGB")
    im = np.array(ImageOps.fit(im, (W, H), Image.LANCZOS, centering=(r.get("crop_x", 0.5), r.get("crop_y", 0.5))))
    mask, bg = cutout(im)
    m3 = mask[..., None]
    fx = []
    for e in r.get("fx", []):
        if e["type"] == "steam": fx.append(Steam(e["x"], e["y"], e.get("w", 0.15)))
        if e["type"] == "snow": fx.append(Snow())
        if e["type"] == "sparkle": fx.append(Sparkle(top=e.get("top", 0.45)))
    hook, _ = text_layers({**r, "caption": "x"})
    caps = [cap_layer(ln, r) for ln in lines]
    end = np.array(Image.open(r["end_card"]).convert("RGB").resize((W, H))).astype(np.float32) / 255
    mv = {"in": (0, 0, 0, 0), "left": (-40, 0, -70, 0), "right": (40, 0, 70, 0)}[r.get("move", "in")]
    n = int(total * FPS)
    n_motion = int(t_end * FPS)
    tmp = out + ".silent.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
                          "-preset", "veryfast", "-crf", "20", tmp], stdin=subprocess.PIPE)
    hook_off = starts[1] - 0.1 if len(starts) > 1 else 3.0
    last = None
    for i in range(n):
        t = i / FPS
        if i < n_motion + int(XF * FPS):
            e = ease(min(1.0, i / max(1, n_motion - 1)))
            b = warp(bg, 1.04 + 0.04 * e, mv[0] * e, mv[1] * e).astype(np.float32) / 255
            fg = warp(im, 1.05 + 0.11 * e, mv[2] * e, 14 * e).astype(np.float32) / 255
            mk = warp(m3, 1.05 + 0.11 * e, mv[2] * e, 14 * e, cv2.BORDER_CONSTANT)[..., None]
            frame = b * (1 - mk) + fg * mk
            if fx:
                layer = np.zeros((H, W), np.float32)
                for f in fx: f.draw(layer, t)
                layer = cv2.GaussianBlur(layer, (0, 0), 6)[..., None]
                frame = frame * (1 - layer) + layer
            if t < hook_off + 0.3:                                   # hook while line 1 is spoken
                frame = over(frame, hook, 1.0 if t < hook_off else max(0, (hook_off + 0.3 - t) / 0.3))
            for j in range(1, len(lines) - 1):                       # middle lines as captions
                a, z = starts[j] - 0.05, starts[j + 1] - 0.1
                if a <= t < z:
                    frame = over(frame, caps[j], min(1.0, (t - a) / 0.15))
            last = frame
        if i >= n_motion:                                             # crossfade to end card
            k = min(1.0, (i - n_motion) / (XF * FPS))
            frame = last * (1 - k) + end * k
        p.stdin.write((np.clip(frame, 0, 1) * 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()

    mix(tmp, vo_path, r["music"], total, r.get("music_vol", 0.10), out)
    os.remove(tmp); os.remove(vo_path)
    Image.fromarray((np.clip(over(warp(im, 1.05, 0, 0).astype(np.float32) / 255, hook), 0, 1) * 255).astype(np.uint8)).save(out.replace(".mp4", "_cover.jpg"), quality=92)
    return total


if __name__ == "__main__":
    r = {**DEFAULTS, **json.load(open(sys.argv[1])), **json.load(open(sys.argv[2]))}
    print("ok", r["out"], round(build(r, r["out"]), 1), "s")
