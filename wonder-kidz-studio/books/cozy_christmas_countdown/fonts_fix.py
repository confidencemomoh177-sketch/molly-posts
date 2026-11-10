"""Replace Type 3 colour emoji and odd symbol fonts with clean embedded TrueType (DejaVu Sans) / vector hearts."""
import pymupdf as fitz
SRC, DST = 'out/Cozy_Christmas_Countdown_Interior.pdf', 'out/fixed.pdf'
DJ, DJB = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
ODD = ('Emoji', 'FreeSerif', 'UnBatang', 'DejaVuSerif')
d = fitz.open(SRC); n = 0
for pg in d:
    spans = [s for b in pg.get_text('dict')['blocks'] if b['type'] == 0 for l in b['lines'] for s in l['spans']
             if any(k in s['font'] for k in ODD) and s['text'].strip()]
    if not spans: continue
    for s in spans:
        r = fitz.Rect(s['bbox']); pg.add_redact_annot(r + (0.3, 0.6, -0.3, -0.6), fill=False)
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    for s in spans:
        t, sz, (x, y) = s['text'], s['size'], s['origin']
        col = tuple(((s['color'] >> k) & 255) / 255 for k in (16, 8, 0))
        if '💚' in t:   # vector heart, green
            h = sz * 0.8; cx, top = x + h / 2, y - h * 0.85
            sh = pg.new_shape()
            sh.draw_bezier((cx, top + h * .95), (cx - h * .9, top + h * .45), (cx - h * .45, top - h * .1), (cx, top + h * .25))
            sh.draw_bezier((cx, top + h * .25), (cx + h * .45, top - h * .1), (cx + h * .9, top + h * .45), (cx, top + h * .95))
            sh.finish(color=None, fill=(0.18, 0.55, 0.30), closePath=True); sh.commit()
            t = t.replace('💚', '').strip()
            if not t: n += 1; continue
            x += h + 2
        bold = 'Bold' in s['font']
        pg.insert_text((x, y), t, fontsize=sz, fontname='djb' if bold else 'dj', fontfile=DJB if bold else DJ, color=col)
        n += 1
d.save(DST, garbage=3, deflate=True); print('replaced', n)
