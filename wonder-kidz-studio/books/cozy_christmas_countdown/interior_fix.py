"""Turn the printable Cozy Christmas Countdown into a B&N paperback interior.
- drop the colour cover page (cover is a separate file) -> 60 pages
- paperback wording instead of "printable/print" wording
- website QR at the front (copyright page) and the back (thank-you page)
- photocopy tip on cut-out pages
- renumber footers"""
import pymupdf as fitz, qrcode, io

SITE = 'wonderkidzstudio.pages.dev'
R = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
B = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
I = '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf'
INK, GREY, MUTE, GREEN = (0x1f/255, 0x24/255, 0x33/255), (0x99/255,)*3, (0x5a/255, 0x5f/255, 0x6e/255), (0x1c/255, 0x4a/255, 0x33/255)


def qr(url):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=20, border=2)
    q.add_data(url); q.make(fit=True); b = io.BytesIO()
    q.make_image(fill_color='black', back_color='white').save(b, 'PNG'); return b.getvalue()


def lines(page, y0, y1):
    return [l['bbox'] for b in page.get_text('dict')['blocks'] if b['type'] == 0 for l in b['lines']
            if l['bbox'][1] >= y0 - 1 and l['bbox'][3] <= y1 + 1]


def wipe(page, rects):
    for r in rects: page.add_redact_annot(fitz.Rect(r), fill=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)


def text(page, rect, s, size=12, font='r', color=INK, align=1, lh=1.2):
    f = {'r': ('lsr', R), 'b': ('lsb', B), 'i': ('lsi', I)}[font]
    r = fitz.Rect(rect); r.y1 += 6
    rc = page.insert_textbox(r, s, fontsize=size, fontname=f[0], fontfile=f[1], color=color, align=align, lineheight=lh)
    assert rc >= 0, (page.number + 1, s[:30], rc)


d = fitz.open('src/countdown.pdf')
d.delete_page(0)          # colour cover page; original page N is now page N-1
P = lambda orig: d[orig - 2]

# copyright page (orig 3)
p = P(3)
wipe(p, lines(p, 108, 225))
text(p, (54, 108, 558, 162), 'No part of this book may be reproduced, stored, or shared in any form without written permission '
     'from the publisher, except that activity pages may be photocopied for use in the buyer\'s own home or classroom.')
text(p, (54, 164, 558, 200), 'Pip, Juniper, Waddles, Grandma Owl and Snuggle Woods are original characters created by Wonder Kidz Studio.')
text(p, (54, 204, 558, 240), 'Grown-ups: some activities use scissors, tape or the kitchen. Please help and supervise little ones.', font='i', color=MUTE)
text(p, (54, 246, 558, 262), 'First edition: 2026 · Published by Wonder Kidz Studio')
p.insert_image(fitz.Rect(256, 276, 356, 376), stream=qr(f'https://{SITE}/'))
text(p, (54, 382, 558, 400), 'Free printables, coloring pages and new books from Pip, Juniper and Waddles:', size=11)
text(p, (54, 398, 558, 416), SITE, size=13, font='b', color=GREEN)

# how it works (orig 5)
p = P(5)
wipe(p, lines(p, 324, 376))
text(p, (54, 324, 558, 378), 'Do one day at a time, or read ahead together. Each day has a short story to read aloud, a picture to '
     'color, an activity and a small kindness mission. Most days take 15–30 minutes. Answers are at the back.', align=0, lh=1.25)

# day 1 paper chain (orig 9)
p = P(9)
wipe(p, lines(p, 106, 124))
text(p, (64, 107, 560, 124), '1. Find the paper chain strips page near the back of this book.', align=0)

# cut-out pages: photocopy tip
TIP = 'Tip: a grown-up can photocopy this page first, so the page on the back stays whole.'
for orig, y in [(23, 528), (31, 512), (49, 528)]:
    text(P(orig), (54, y, 558, y + 16), TIP, size=11, font='i', color=MUTE, align=0)
p = P(58)
text(p, (54, 662, 558, 678), TIP, size=11, font='i', color=MUTE)

# thank-you page (orig 61)
p = P(61)
wipe(p, lines(p, 400, 470))
text(p, (54, 401, 558, 418), SITE, size=14, font='b')
text(p, (54, 440, 558, 474), 'Grown-ups: if your family enjoyed this book, a short Barnes & Noble review helps other families find us. Thank you!',
     font='i', color=MUTE)
img = [i for i in p.get_images(full=True) if True]
for im in img:
    r = p.get_image_rects(im[0])
    if r and abs(r[0].x0 - 220) < 5 and abs(r[0].y0 - 219) < 5:
        p.replace_image(im[0], stream=qr(f'https://{SITE}/#free'))

# footers: renumber
for i, pg in enumerate(d):
    fr = [l for l in lines(pg, 750, 770)]
    if not fr: continue
    wipe(pg, fr)
    s = f'Cozy Christmas Countdown  ·  Wonder Kidz Studio  ·  {i + 1}'
    text(pg, (100, 754, 512, 768), s, size=8, color=GREY)

d.set_metadata({'title': 'Cozy Christmas Countdown: A 25-Day Advent Activity Calendar for Kids', 'author': 'Wonder Kidz Studio',
                'creator': 'Wonder Kidz Studio', 'producer': '', 'subject': '', 'keywords': ''})
d.save('out/Cozy_Christmas_Countdown_Interior.pdf', garbage=3, deflate=True)
print('pages', len(d))
