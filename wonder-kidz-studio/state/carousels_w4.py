"""Week 4 (23-29 Nov): 4 carousel-style posts, rendered as slides AND as music videos
(week-2 review: silent photo carousels got almost no reach; videos get FYP/Reels reach).
Usage: python3 carousels_w4.py  -> carousels_w4/NN_key/{ig,tt}_SS.jpg + video.mp4"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carousel import *  # noqa  (slide, tiktok, page, C, split, CTA_ACT, CTA_COL, build, REPO, ACT, GREEN, RED)
import pymupdf as fitz
from PIL import Image

# SEN = "/home/claude/molly-posts/wonder-kidz-studio/books/large_print_seniors_interior.pdf"
def sen(n):
    d = fitz.open(SEN); pix = d[n - 1].get_pixmap(dpi=110)
    from carousel import trim
    return trim(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
# COVER_SEN = Image.open(f"{REPO}/site/img/large-print-christmas-word-search-for-seniors.jpg").convert("RGB")

CDN = "/home/claude/molly-posts/wonder-kidz-studio/books/cozy_christmas_countdown/Cozy_Christmas_Countdown_Interior.pdf"
def cdn(n):
    d = fitz.open(CDN); pix = d[n - 1].get_pixmap(dpi=110)
    from carousel import trim
    return trim(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
IMG = f"{REPO}/site/img"
COV = lambda f: Image.open(f"{IMG}/{f}").convert("RGB")
CP = f"{REPO}/colored_pages"
BA = lambda k: split(f"{CP}/{k}_lines.png", f"{CP}/{k}_colored.png")

CAROUSELS = [
 dict(key="kids_table", date="2026-11-23", music="christmas_we_wish_musicbox.wav", slides=[
   dict(kicker="Hosting Thanksgiving?", title="3 quiet puzzles for the kids' table", body="Print them before Thursday!", img=page(ACT, 34), tsize=68),
   dict(kicker="Puzzle 1", title="Spot Five Differences", body="Circle 5 things that are different in the bottom picture.", img=page(ACT, 34)),
   dict(kicker="Puzzle 2", title="Christmas Picture Sudoku", body="A tree, a bell, a gift and a mitten in every row, column and box.", img=page(ACT, 47), bsize=33),
   dict(kicker="Puzzle 3", title="Connect 1 to 15", body="What does Juniper want to decorate?", img=page(ACT, 16)),
   CTA_ACT]),
 dict(key="before_after", date="2026-11-25", music="children_bright_xylophone.wav", slides=[
   dict(kicker="Before & after", title="Which one would your kid color first?", body="1, 2 or 3? Pages from our Cozy Christmas coloring story", img=BA("tree_top"), tsize=66),
   dict(kicker="Page 13 of 50", title="The star on top", img=BA("tree_top")),
   dict(kicker="Page 40 of 50", title="A letter to Santa", img=BA("letter_mailbox")),
   dict(kicker="Page 45 of 50", title="Christmas morning", img=BA("christmas_morning")),
   CTA_COL]),
 dict(key="black_friday_gifts", date="2026-11-27", music="christmas_jingle_bells_bells.wav", slides=[
   dict(kicker="Black Friday gift list", title="3 cozy Christmas books for every age", body="Paperbacks · $14.99 each at Barnes & Noble", img=COV("cozy-christmas-coloring-book-paperback.jpg"), tsize=66),
   dict(kicker="Ages 3–8", title="Cozy Christmas Coloring Book", body="50 story pages that end on Christmas Day.", img=COV("cozy-christmas-coloring-book-paperback.jpg")),
   dict(kicker="Ages 4–8", title="Cozy Christmas Activity Book", body="Mazes, I Spy, dot-to-dots, puzzles and more.", img=COV("cozy-christmas-activity-book-paperback.jpg")),
   dict(kicker="For Grandma & Grandpa", title="Large Print Christmas Word Search", body="100 puzzles in large print.", img=COV("large-print-christmas-word-search-for-seniors.jpg")),
   dict(bg=GREEN, kicker="Barnes & Noble", title="Paperbacks · $14.99", body="Links to all our Christmas books: link in bio.", img=COV("cozy-christmas-activity-book-paperback.jpg"), foot="Save this gift list")]),
 dict(key="advent_countdown", date="2026-11-29", music="christmas_we_wish_piano.wav", slides=[
   dict(kicker="Advent starts Tuesday!", title="25 days of cozy Christmas fun", body="Cozy Christmas Countdown · December 1st to 25th", img=COV("cozy-christmas-countdown.jpg"), tsize=68),
   dict(kicker="Every day", title="A story, a picture and an activity", body="Plus a Kindness Mission to share.", img=cdn(13), bsize=34),
   dict(kicker="Find the stars", title="Color one star each day", body="When all 25 are colored, the lantern is full!", img=cdn(6)),
   dict(kicker="Day 10", title="Kindness bingo", body="Give a hug, say thank you, help set the table…", img=cdn(26), bsize=34),
   dict(bg=RED, kicker="Cozy Christmas Countdown", title="Start on December 1st", body="Ages 4–8 · most days take 15–30 minutes.\nLink in bio.", img=COV("cozy-christmas-countdown.jpg"), foot="Save this for Tuesday")]),
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
    out = f"{REPO}/carousels_w4"
    build(CAROUSELS, out, sys.argv[1:])
    for n, c in enumerate(CAROUSELS):
        if sys.argv[1:] and c["key"] not in sys.argv[1:]: continue
        print(c["key"], round(video(f"{out}/{n+1:02d}_{c['key']}", c["music"]), 1), "s")
