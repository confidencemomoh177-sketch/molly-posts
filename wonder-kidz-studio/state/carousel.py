"""Build swipeable carousels (Instagram 1080x1350, TikTok 1080x1920) for Wonder Kidz Studio.
Usage: python3 carousel.py  -> writes carousels_w2/NN_key/{ig,tt}_SS.jpg"""
import os, json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
G = "/usr/share/fonts/truetype/google-fonts/"
CREAM, RED, GREEN, GOLD, INK = "#FCF6EB", "#C62033", "#1C4A33", "#FFD257", "#1F2433"
ACT, COL = "/home/claude/cozy/activity.pdf", "/home/claude/cozy/coloring.pdf"
CP = f"{REPO}/colored_pages"
LOGO = "/home/claude/cozy/persona/wonderkidz_logo_300.png"
CACHE = "/home/claude/wk/pages"


def F(name, size, w=None):
    f = ImageFont.truetype(G + name, size)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f


def wrap(d, text, f, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out


def ctext(d, text, f, y, W, fill, maxw, lh=1.18, x0=0):
    for ln in wrap(d, text, f, maxw):
        d.text((x0 + (W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=fill); y += int(f.size * lh)
    return y


def page(pdf, n):
    pre = "a" if pdf == ACT else "c"
    p = f"{CACHE}/{pre}-{n}.png"
    if not os.path.exists(p):
        subprocess.run(["pdftoppm", "-f", str(n), "-l", str(n), "-r", "150", "-png", "-singlefile", pdf, p[:-4]], check=True)
    return trim(Image.open(p).convert("RGB"))


def trim(im, pad=18):
    g = ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 30 else 0)
    bb = g.getbbox()
    if not bb: return im
    x0, y0, x1, y1 = bb
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def card(img, maxw, maxh, radius=28, border=0):
    img = img.copy(); img.thumbnail((maxw, maxh), Image.LANCZOS)
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *img.size), radius, fill=255)
    out = Image.new("RGBA", (img.width + 40, img.height + 40), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0); ImageDraw.Draw(sh).rounded_rectangle((20, 26, 20 + img.width, 26 + img.height), radius, fill=70)
    out.putalpha(sh.filter(ImageFilter.GaussianBlur(12)))
    out = Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), Image.new("RGBA", out.size, (0, 0, 0, 0)), out.getchannel("A"))
    out.paste(img, (20, 20), m)
    if border:
        ImageDraw.Draw(out).rounded_rectangle((20, 20, 20 + img.width, 20 + img.height), radius, outline=RED, width=border)
    return out


def split(lines, colored):
    a = Image.open(lines).convert("RGB"); b = Image.open(colored).convert("RGB").resize(a.size)
    m = Image.new("L", a.size, 0); ImageDraw.Draw(m).polygon([(a.width * .55, 0), (a.width, 0), (a.width, a.height), (a.width * .45, a.height)], fill=255)
    out = a.copy(); out.paste(b, (0, 0), m)
    d = ImageDraw.Draw(out); f = F("Poppins-Bold.ttf", int(a.width * .045))
    for txt, x, col in [("BEFORE", a.width * .04, INK), ("AFTER", a.width * .78, RED)]:
        tw = d.textlength(txt, font=f); y = a.height * .035
        d.rounded_rectangle((x - 14, y - 6, x + tw + 14, y + f.size * 1.25), 14, fill="white", outline=col, width=4)
        d.text((x, y), txt, font=f, fill=col)
    return out


def slide(s, i, n, W=1080, H=1350):
    bg = s.get("bg", CREAM)
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    dark = bg in (RED, GREEN)
    fg = "white" if dark else INK
    # header chip
    lg = Image.open(LOGO).convert("RGBA"); lg.thumbnail((70, 70))
    im.paste(lg, (48, 40), lg)
    d.text((132, 58), "WONDER KIDZ STUDIO", font=F("Poppins-Bold.ttf", 26), fill=GOLD if dark else RED)
    cnt = f"{i}/{n}"; fc = F("Poppins-Medium.ttf", 26)
    d.rounded_rectangle((W - 48 - d.textlength(cnt, font=fc) - 36, 50, W - 48, 100), 25, fill=GOLD if not dark else "white")
    d.text((W - 48 - d.textlength(cnt, font=fc) - 18, 57), cnt, font=fc, fill=INK)
    y = 150
    if s.get("kicker"):
        fk = F("Poppins-Bold.ttf", 30); t = s["kicker"].upper(); tw = d.textlength(t, font=fk)
        d.rounded_rectangle(((W - tw) / 2 - 22, y - 6, (W + tw) / 2 + 22, y + 46), 26, fill=RED if not dark else GOLD)
        d.text(((W - tw) / 2, y), t, font=fk, fill="white" if not dark else INK); y += 76
    ft = F("Lora-Variable.ttf", s.get("tsize", 74), 700)
    y = ctext(d, s["title"], ft, y, W, "white" if dark else GREEN, W - 140, lh=1.12) + 14
    if s.get("body"):
        y = ctext(d, s["body"], F("Poppins-Medium.ttf", s.get("bsize", 36)), y, W, fg, W - 160, lh=1.35) + 10
    foot = 1350 - 110
    if s.get("img") is not None:
        c = card(s["img"], W - 140, foot - y - 30, border=s.get("border", 0))
        im.paste(c, ((W - c.width) // 2, y + (foot - y - c.height) // 2 + 6), c)
    if s.get("covers"):
        cs = [card(c, 380, foot - y - 40, radius=14) for c in s["covers"]]
        tot = sum(c.width for c in cs) - 30 * (len(cs) - 1); x = (W - tot) // 2
        for c in cs:
            im.paste(c, (x, y + (foot - y - c.height) // 2), c); x += c.width - 30
    ff = F("Poppins-Bold.ttf", 30)
    ft2 = s.get("foot", "Swipe →" if i == 1 else ("" if i == n else "Swipe for more →"))
    if ft2:
        arrow = "→" in ft2; ft2 = ft2.replace("→", "").replace("♡", "").strip()
        tw = d.textlength(ft2, font=ff) + (40 if arrow else 0)
        col = "white" if not dark else INK
        d.rounded_rectangle(((W - tw) / 2 - 28, H - 92, (W + tw) / 2 + 28, H - 38), 27, fill=GREEN if not dark else GOLD)
        d.text(((W - tw) / 2, H - 87), ft2, font=ff, fill=col)
        if arrow:
            ax = (W + tw) / 2 - 22; ay = H - 65
            d.line((ax - 10, ay, ax + 12, ay), fill=col, width=5)
            d.polygon([(ax + 20, ay), (ax + 6, ay - 11), (ax + 6, ay + 11)], fill=col)
    return im


def tiktok(ig):
    W, H = 1080, 1920
    bg = ig.getpixel((5, 300))
    out = Image.new("RGB", (W, H), bg); out.paste(ig, (0, (H - ig.height) // 2 - 40))
    return out


C = lambda k: Image.open(f"{CP}/{k}_colored.png").convert("RGB")
CTA_ACT = dict(bg=GREEN, kicker="Free for you", title="34 free Christmas printables",
               body="Mazes, I Spy, gift tags, an advent coloring calendar and more.\nTap the link in our bio to download.",
               img=C("christmas_morning"), foot="Save this for later ♡")
CTA_COL = dict(bg=RED, kicker="Cozy Christmas", title="50 pages. One cozy Christmas story.",
               body="Coloring book for ages 3–8, plus 34 free printables.\nLink in bio.", img=Image.open(f"{REPO}/site/img/cozy-christmas-coloring-book-paperback.jpg"), foot="Save this for later ♡")

CAROUSELS = [
 dict(key="screen_free_5", date="2026-11-09", slides=[
   dict(kicker="No prep · ages 4–8", title="4 screen-free Christmas activities for this week", img=C("tree_sled"), tsize=70),
   dict(kicker="1 · Maze", title="Find the Sled!", body="Help Waddles reach his sled. Use a pencil so they can erase and try again.", img=page(ACT, 7)),
   dict(kicker="2 · Spot the difference", title="Spot Five Differences", body="Look closely! Circle 5 things that are different.", img=page(ACT, 29)),
   dict(kicker="3 · Quiet time", title="Christmas Color by Number", body="Color each numbered area using the key.", img=page(ACT, 63)),
   dict(kicker="4 · Family game", title="Christmas Tic-Tac-Toe", body="One player draws stars, the other draws mittens.", img=page(ACT, 69)),
   CTA_ACT]),
 dict(key="meet_friends", date="2026-11-10", slides=[
   dict(kicker="Snuggle Woods", title="Meet the three friends getting ready for Christmas", img=C("christmas_morning"), tsize=68),
   dict(kicker="Pip the bear cub", title="Cocoa, cookies and big hugs", body="His striped scarf goes everywhere with him.", img=C("hot_cocoa")),
   dict(kicker="Juniper the bunny", title="She loves making things", body="Her pom-pom hat bounces when she hops!", img=C("paper_chain")),
   dict(kicker="Waddles the penguin", title="Snow, sleds and silly jokes", body="His earmuffs keep him toasty.", img=C("sledding")),
   dict(kicker="Their Christmas", title="From first snowfall to Christmas morning", body="Follow their story page by page, with a hidden star on every page.", img=C("its_snowing")),
   CTA_COL]),
 dict(key="before_after", date="2026-11-11", slides=[
   dict(kicker="Swipe to see", title="From black & white to full color", body="Which one would your little artist color first?", img=split(f"{CP}/gingerbread_house_lines.png", f"{CP}/gingerbread_house_colored.png"), tsize=70),
   dict(kicker="Page 3", title="The biggest snowman", img=split(f"{CP}/snowman_lines.png", f"{CP}/snowman_colored.png")),
   dict(kicker="Page 15", title="Three stockings by the fire", img=split(f"{CP}/stockings_lines.png", f"{CP}/stockings_colored.png")),
   dict(kicker="Page 18", title="Stir, stir, stir!", img=split(f"{CP}/cookie_dough_lines.png", f"{CP}/cookie_dough_colored.png")),
   dict(kicker="Page 41", title="Cookies and milk for Santa", img=split(f"{CP}/christmas_eve_lines.png", f"{CP}/christmas_eve_colored.png")),
   CTA_COL]),
 dict(key="coloring_tips", date="2026-11-12", slides=[
   dict(kicker="For grown-ups", title="5 tips for happy little artists", img=C("ornaments"), tsize=72),
   dict(kicker="Tip 1", title="Crayons & colored pencils for ages 3–5", body="Using markers? Slip a sheet of paper behind the page, just in case.", img=C("snowman")),
   dict(kicker="Tip 2", title="One page a day", body="Color one page a day as a Christmas countdown, or as many as you want!", img=C("stockings")),
   dict(kicker="Tip 3", title="There is no wrong color", body="A purple bear? A rainbow penguin? Yes, please!", img=C("gingerbread_house")),
   dict(kicker="Tip 4", title="Ask while they color", body="“What is Pip doing? What color should the cocoa be?” It builds language and storytelling skills.", img=C("hot_cocoa"), bsize=33),
   dict(kicker="Tip 5", title="Turn pages into cards", body="Pages are single-sided, so finished pictures can be cut out and hung on the fridge or given as Christmas cards.", img=C("christmas_cards"), bsize=33),
   CTA_COL]),
 dict(key="brain_games", date="2026-11-13", slides=[
   dict(kicker="Ages 4–8", title="4 Christmas brain games for little thinkers", img=page(ACT, 45), tsize=70),
   dict(kicker="1 · Shadows", title="Christmas Shadows", body="Match each object to its shadow.", img=page(ACT, 36)),
   dict(kicker="2 · Odd one out", title="Which One Is Different?", body="Circle the odd one in each row.", img=page(ACT, 37)),
   dict(kicker="3 · Matching", title="Find the Pairs", body="Draw a line between matching mittens.", img=page(ACT, 39)),
   dict(kicker="4 · Logic", title="Christmas Picture Sudoku", body="Every row, column and 2 × 2 box needs one tree, one bell, one gift and one star.", img=page(ACT, 46), bsize=33),
   CTA_ACT]),
 dict(key="story_5", date="2026-11-14", slides=[
   dict(kicker="Swipe the story", title="A cozy Christmas in 5 pages", img=C("tree_top"), tsize=76),
   dict(kicker="Page 1", title="“It's snowing!”", body="One morning, Waddles woke up and gasped.", img=C("its_snowing")),
   dict(kicker="Page 3", title="Roll, roll, roll!", body="They built the biggest snowman in Snuggle Woods.", img=C("snowman")),
   dict(kicker="Page 17", title="Gingerbread time!", body="Candy, icing and gumdrops: time for a gingerbread house!", img=C("gingerbread_house")),
   dict(kicker="Page 41", title="It's Christmas Eve!", body="Cookies and milk for Santa.", img=C("christmas_eve")),
   dict(kicker="Page 45", title="Christmas morning!", body="The friends raced to the tree.", img=C("christmas_morning")),
   CTA_COL]),
 dict(key="gift_guide", date="2026-11-15", slides=[
   dict(kicker="Gift guide", title="A cozy Christmas book for every age", body="Paperbacks at Barnes & Noble · $14.99 each",
        covers=[Image.open(f"{REPO}/site/img/{n}").convert("RGB") for n in ["cozy-christmas-coloring-book-paperback.jpg", "cozy-christmas-activity-book-paperback.jpg", "large-print-christmas-word-search-for-seniors.jpg"]], tsize=70),
   dict(kicker="Ages 3–8", title="Cozy Christmas Coloring Book", body="The friends' whole Christmas, from first snowfall to Christmas morning. 34-page free bundle inside.", img=Image.open(f"{REPO}/site/img/cozy-christmas-coloring-book-paperback.jpg"), bsize=33),
   dict(kicker="Ages 4–8", title="Cozy Christmas Activity Book", body="Mazes, dot-to-dot, I Spy, word search and spot-the-difference.", img=Image.open(f"{REPO}/site/img/cozy-christmas-activity-book-paperback.jpg"), bsize=33),
   dict(kicker="For grandparents", title="Large Print Christmas Word Search", body="100 festive puzzles, an advent countdown and three gentle levels, each on its own full page.", img=Image.open(f"{REPO}/site/img/large-print-christmas-word-search-for-seniors.jpg"), bsize=33),
   dict(kicker="Stocking stuffers", title="Screen-free fun for the whole family", body="Color, puzzle and play together this Christmas.", img=C("secret_presents")),
   dict(bg=GREEN, kicker="Shop", title="All three on our website", body="Links to every paperback, plus free printables.\nLink in bio.", covers=[Image.open(f"{REPO}/site/img/{n}").convert("RGB") for n in ["cozy-christmas-coloring-book-paperback.jpg", "cozy-christmas-activity-book-paperback.jpg", "large-print-christmas-word-search-for-seniors.jpg"]], foot="Save this gift list ♡")]),
]

if __name__ == "__main__":
    import sys
    only = sys.argv[1:]
    for n, c in enumerate(CAROUSELS):
        if only and c["key"] not in only: continue
        out = f"{REPO}/carousels_w2/{n+1:02d}_{c['key']}"; os.makedirs(out, exist_ok=True)
        for f in os.listdir(out): os.remove(f"{out}/{f}")
        k = len(c["slides"])
        for i, s in enumerate(c["slides"], 1):
            ig = slide(s, i, k)
            ig.save(f"{out}/ig_{i:02d}.jpg", quality=90); tiktok(ig).save(f"{out}/tt_{i:02d}.jpg", quality=90)
        print(out, k)
