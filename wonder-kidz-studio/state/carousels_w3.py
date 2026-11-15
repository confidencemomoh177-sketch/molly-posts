"""Week 3 (16-22 Nov): 4 carousel-style posts, rendered as slides AND as music videos
(week-2 review: silent photo carousels got almost no reach; videos get FYP/Reels reach).
Usage: python3 carousels_w3.py  -> carousels_w3/NN_key/{ig,tt}_SS.jpg + video.mp4"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carousel import *  # noqa  (slide, tiktok, page, C, split, CTA_ACT, CTA_COL, build, REPO, ACT, GREEN, RED)
import pymupdf as fitz
from PIL import Image

SEN = "/home/claude/molly-posts/wonder-kidz-studio/books/large_print_seniors_interior.pdf"
def sen(n):
    d = fitz.open(SEN); pix = d[n - 1].get_pixmap(dpi=110)
    from carousel import trim
    return trim(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
COVER_SEN = Image.open(f"{REPO}/site/img/large-print-christmas-word-search-for-seniors.jpg").convert("RGB")

CAROUSELS = [
 dict(key="spot_difference", date="2026-11-16", music="christmas_jingle_bells_musicbox.wav", slides=[
   dict(kicker="Look closely!", title="Can your kid spot all 5 differences?", body="3 Christmas puzzles. Ready, set, go!", img=page(ACT, 30), tsize=70),
   dict(kicker="Puzzle 1", title="Spot Five Differences", body="Circle 5 things that are different in the bottom picture.", img=page(ACT, 30)),
   dict(kicker="Puzzle 2", title="Spot Five Differences", body="The Christmas Fair is almost ready. Look closely!", img=page(ACT, 31)),
   dict(kicker="Puzzle 3", title="Spot Five Differences", body="How fast can your kid find all 5?", img=page(ACT, 32)),
   CTA_ACT]),
 dict(key="color_by_number", date="2026-11-18", music="children_bright_musicbox.wav", slides=[
   dict(kicker="Quiet time", title="3 Christmas color by number pages", body="Color each numbered area using the key.", img=page(ACT, 64), tsize=70),
   dict(kicker="Page 1", title="Color by Number", img=page(ACT, 64)),
   dict(kicker="Page 2", title="Color by Number", img=page(ACT, 65)),
   dict(kicker="Page 3", title="Color by Number", img=page(ACT, 66)),
   CTA_ACT]),
 dict(key="grandparents_gift", date="2026-11-20", music="christmas_we_wish_strings.wav", slides=[
   dict(kicker="Gift idea", title="A Christmas gift for Grandma & Grandpa", body="Large Print Christmas Word Search for Seniors", img=COVER_SEN, tsize=68),
   dict(kicker="100 puzzles", title="Large print, one puzzle per page", body="Each page shows its level at the top: Easy, Medium or Challenge.", img=sen(51), bsize=33),
   dict(kicker="Memories", title="A Christmas memory on every page", body="“Do you remember the first ornament you ever hung?”", img=sen(9)),
   dict(kicker="Advent countdown", title="25 Days of Advent", body="One puzzle for each day from December 1st to Christmas Day.", img=sen(87)),
   dict(bg=GREEN, kicker="Barnes & Noble", title="Paperback · $14.99", body="Links to all our Christmas books: link in bio.", img=COVER_SEN, foot="Save this gift idea")]),
 dict(key="trace_write", date="2026-11-22", music="children_twinkle_musicbox.wav", slides=[
   dict(kicker="Little writers", title="3 Christmas handwriting pages", body="Trace the words, then the numbers.", img=page(ACT, 51), tsize=72),
   dict(kicker="Page 1", title="TREE · STAR · GIFT", img=page(ACT, 51)),
   dict(kicker="Page 2", title="SNOW · BELL · SLED", img=page(ACT, 52)),
   dict(kicker="Page 3", title="Trace the numbers 1–10", img=page(ACT, 55)),
   CTA_ACT]),
]

SLIDE_S, FADE = 3.2, 0.45


def video(folder, music):
    tts = sorted(f for f in os.listdir(folder) if f.startswith("tt_"))
    n = len(tts); dur = n * SLIDE_S - (n - 1) * FADE
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for f in tts: args += ["-loop", "1", "-t", str(SLIDE_S), "-i", f"{folder}/{f}"]
    args += ["-i", f"/home/claude/wk/music/{music}"]
    fc, last = [], "[0:v]"
    for i in range(1, n):
        off = i * (SLIDE_S - FADE)
        out = f"[v{i}]"; fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={FADE}:offset={off:.2f}{out}"); last = out
    fc.append(f"{last}format=yuv420p,scale=1080:1920[vout]")
    fc.append(f"[{n}:a]atrim=0:{dur:.2f},afade=t=out:st={dur-1.5:.2f}:d=1.5[aout]")
    args += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]", "-r", "30", "-c:v", "libx264",
             "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", f"{folder}/video.mp4"]
    subprocess.run(args, check=True)
    return dur


if __name__ == "__main__":
    for c in CAROUSELS:  # videos: no "swipe" buttons
        c["slides"] = [dict(x, foot=x.get("foot", "")) if i < len(c["slides"]) - 1 else x for i, x in enumerate(c["slides"])]
    out = f"{REPO}/carousels_w3"
    build(CAROUSELS, out, sys.argv[1:])
    for n, c in enumerate(CAROUSELS):
        if sys.argv[1:] and c["key"] not in sys.argv[1:]: continue
        print(c["key"], round(video(f"{out}/{n+1:02d}_{c['key']}", c["music"]), 1), "s")
