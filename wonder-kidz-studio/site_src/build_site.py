"""Builds the Wonder Kidz Studio website into ../site from products.json and the parts in this folder.

Run:  python3 build_site.py      (then commit and push; Netlify publishes ../site)
To add a product: put its cover in ../site/img/<slug>.jpg (square, ~1000px) and add an entry to products.json.
"""
import json, html, os, re, datetime
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'site')
SITE = 'https://wonderkidzstudio.netlify.app'
BRAND = 'Wonder Kidz Studio'
TODAY = datetime.date.today().isoformat()

P = json.load(open(os.path.join(HERE, 'products.json')))
BY = {p['slug']: p for p in P}
FREE = json.load(open(os.path.join(HERE, 'free_pages.json')))
FAQ = json.load(open(os.path.join(HERE, 'faq.json')))
part = lambda n: open(os.path.join(HERE, n)).read()
STYLES, SPRITE, NAV, FOOTER, SCRIPTS = part('head_styles.html'), part('part_sprite.html'), part('part_nav.html'), part('part_footer.html'), part('part_scripts.html')
e = lambda s: html.escape(s, quote=True)

EXTRA_CSS = """<style>
html{scroll-behavior:smooth}
.cover-wrap{position:relative}
.cover-wrap>a{display:block}
.pin-btn{position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;gap:6px;background:#E60023;color:#fff!important;font-weight:800;font-size:.82rem;
  padding:6px 12px 6px 9px;border-radius:999px;text-decoration:none;box-shadow:0 2px 0 rgba(0,0,0,.25);z-index:2}
.pin-btn svg{width:16px;height:16px;fill:#fff}
.pin-btn:hover{background:#ad081b}
.feature-pack h3 a{color:inherit;text-decoration:none}
.feature-pack h3 a:hover{text-decoration:underline}
.more-link{font-weight:700;font-size:.9rem;color:var(--ink-soft,#5a5f6e);text-decoration:underline;text-underline-offset:3px}
.pp-section{padding:28px 0 56px}
.crumbs{font-size:.9rem;color:var(--ink-soft,#5a5f6e);margin:0 0 22px}
.crumbs a{color:inherit}
.pp{display:grid;grid-template-columns:minmax(0,460px) 1fr;gap:44px;align-items:start}
.pp-cover img{width:100%;height:auto;aspect-ratio:1/1;border:3px solid #1f2433;border-radius:16px;box-shadow:0 8px 0 #1f2433;display:block}
.pp-info{display:grid;gap:14px;align-content:start}
.pp-info h1{margin:0;line-height:1.1;font-size:clamp(1.9rem,3.6vw,2.7rem)}
.pp-price{font-size:1.6rem;font-weight:800;margin:0}
.pp-price .was{font-size:1rem;margin-left:10px}
.pp-info p.lead{font-size:1.08rem;color:var(--ink-soft,#5a5f6e);margin:0}
.pp-info ul{margin:0;padding-left:1.2em;display:grid;gap:6px}
.pp-buy{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:6px}
.pp-buy .btn{font-size:1.08rem;padding:14px 26px}
.pp-note{font-size:.9rem;color:var(--ink-soft,#5a5f6e);margin:0}
.pp-incl{border:2px dashed #b9b2a3;border-radius:14px;padding:16px 18px;display:grid;gap:10px}
.pp-incl h2{font-size:1.05rem;margin:0}
.pp-incl a{display:flex;gap:12px;align-items:center;color:inherit;text-decoration:none;font-weight:700}
.pp-incl img{width:56px;height:56px;border-radius:8px;border:2px solid #1f2433}
.pp-more{margin-top:56px}
.pp-more h2{margin:0 0 18px}
@media (max-width:820px){.pp{grid-template-columns:1fr;gap:26px}.pp-cover{max-width:460px}}
.nf{min-height:60vh;display:grid;place-items:center;text-align:center;padding:60px 16px}
.xmas-bar{background:#C62033;color:#fff;font-weight:700;font-size:.95rem;text-align:center;padding:9px 44px;position:relative;line-height:1.35}
.xmas-bar a{color:#fff;text-decoration:underline;text-underline-offset:3px}
.xmas-bar .num{background:#FFD257;color:#1f2433;border-radius:8px;padding:1px 8px;margin:0 2px;font-weight:800}
.xmas-bar button{position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:0;color:#fff;font-size:1.3rem;cursor:pointer;padding:4px 8px;line-height:1}
.free-pages{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.free-card{background:var(--card,#fff);border:3px solid #1f2433;border-radius:var(--r,18px);box-shadow:0 6px 0 #1f2433;padding:18px;display:grid;grid-template-columns:180px 1fr;gap:18px;align-items:center}
.free-card img{width:100%;height:auto;border:2px solid #1f2433;border-radius:8px;background:#fff;display:block}
.free-card .body{display:grid;gap:8px;align-content:start}
.free-card h3{margin:0}
.free-card p{margin:0;color:var(--ink-soft,#5a5f6e);font-size:.98rem}
.free-card .btn{justify-self:start;margin-top:6px}
#free-pages,#faq,#shop,#parents,#free{scroll-margin-top:90px}
@media (max-width:900px){.free-pages{grid-template-columns:1fr}}
@media (max-width:480px){.free-card{grid-template-columns:110px 1fr;gap:14px;padding:14px}}
.signup-band{background:#1C4A33;color:#fff;border-block:3px solid #1f2433}
.signup{display:grid;grid-template-columns:1.1fr 1fr;gap:32px;align-items:center}
.signup-band .eyebrow{color:#FFD257}
.signup-band h2{color:#fff;margin:6px 0 10px}
.signup-text p{color:#cfe3dc;margin:0}
.signup-form{display:grid;grid-template-columns:1fr auto;gap:12px}
.signup-form input[type=email]{font:inherit;font-size:1.05rem;padding:14px 16px;border:3px solid #1f2433;border-radius:12px;min-width:0}
.signup-form .btn{white-space:nowrap}
.signup-msg{grid-column:1/-1;margin:0;font-weight:700;min-height:1.2em}
.signup-msg.ok{color:#FFD257}.signup-msg.err{color:#ffb3b3}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
#signup{scroll-margin-top:90px}
@media (max-width:820px){.signup{grid-template-columns:1fr;gap:18px}}
@media (max-width:420px){.signup-form{grid-template-columns:1fr}}
.faq{display:grid;gap:12px;max-width:820px}
.faq details{background:var(--card,#fff);border:2px solid #1f2433;border-radius:14px;padding:14px 18px}
.faq summary{font-weight:800;cursor:pointer;font-size:1.05rem;list-style:none;display:flex;justify-content:space-between;gap:12px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-size:1.3rem;line-height:1}
.faq details[open] summary::after{content:"–"}
.faq details p{margin:10px 0 0;color:var(--ink-soft,#5a5f6e)}
.nf svg.pip{width:140px;height:160px}
</style>"""

PIN_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.6 19.3c-.1-.8-.2-2.1 0-3l1.2-5s-.3-.6-.3-1.5c0-1.4.8-2.5 1.8-2.5.9 0 1.3.7 1.3 1.4 0 .9-.6 2.2-.9 3.4-.2 1 .5 1.9 1.6 1.9 1.9 0 3.3-2 3.3-4.9 0-2.6-1.8-4.4-4.5-4.4-3 0-4.8 2.3-4.8 4.6 0 .9.4 1.9.8 2.4.1.1.1.2.1.3l-.3 1.2c0 .2-.2.3-.4.2-1.4-.7-2.3-2.7-2.3-4.3 0-3.5 2.6-6.8 7.4-6.8 3.9 0 6.9 2.8 6.9 6.5 0 3.9-2.4 7-5.8 7-1.1 0-2.2-.6-2.6-1.3l-.7 2.7c-.3 1-1 2.3-1.4 3.1A10 10 0 1 0 12 2z"/></svg>'


def page_url(p): return f"{SITE}/{p['slug']}/"


def pin_link(p):
    from urllib.parse import quote
    desc = f"{p['title']}: {p['desc']}"
    return ("https://www.pinterest.com/pin/create/button/?url=" + quote(page_url(p), safe='') +
            "&media=" + quote(f"{SITE}/{p['img']}", safe='') + "&description=" + quote(desc[:480], safe=''))


def buy_btn(p, big=False):
    return (f'<a class="btn berry" href="{e(p["gumroad"])}" data-gumroad-overlay-checkout="true">{e(p["button"])}</a>')


def card(p, small_img=True):
    img = f"/img/{p['slug']}-480.jpg" if small_img and not p.get('featured') else f"/{p['img']}"
    cls = 'feature-pack bundle' if p.get('featured') else 'feature-pack'
    badge = f' <span class="save-badge">{e(p["badge"])}</span>' if p.get('badge') else ''
    was = f'<span class="was">{e(p["was"])}</span>' if p.get('was') else ''
    lis = ''.join(f'<li>{e(b)}</li>' for b in p['bullets'])
    return f'''<article class="{cls}">
        <div class="cover-wrap"><a href="/{p['slug']}/"><img src="{img}" alt="{e(p['alt'])}" width="600" height="600" loading="lazy"></a>
          <a class="pin-btn" href="{e(pin_link(p))}" target="_blank" rel="noopener" aria-label="Save {e(p['title'])} to Pinterest">{PIN_SVG}Save</a></div>
        <div class="body">
          <span class="tag on">{e(p['tag'])}</span>
          <h3><a href="/{p['slug']}/">{e(p['title'])}</a>{badge}</h3>
          <p>{e(p['desc'])}</p>
          <ul>{lis}</ul>
          <div class="foot">{buy_btn(p)}{was}<a class="more-link" href="/{p['slug']}/">Details</a></div>
        </div>
      </article>'''


def section_html(sec):
    items = [p for p in P if p['section'] == sec]
    feat = ''.join(card(p) for p in items if p.get('featured'))
    grid = ''.join(card(p) for p in items if not p.get('featured'))
    return feat + f'\n      <div class="product-grid">\n      {grid}\n      </div>'


def head(title, desc, url, image, og_type='website', extra_meta='', jsonld=None):
    j = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#1C4A33">
<meta name="p:domain_verify" content="a2a2ac66b967b897bfebe380d8e60487"/>
<meta name="msvalidate.01" content="80057D46B34606854118D2A22715B657" />
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "aff9a899a42748abaa16e0ecc21952e8"}}'></script>
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{image}">
{extra_meta}
<style>:root{{color-scheme:light}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{STYLES}
{EXTRA_CSS}
{j}
</head>
<body>
'''


def rel_nav(s):  # nav/footer anchors point back to the homepage sections
    return re.sub(r'(<a\b[^>]*?)href="#', r'\1href="/#', s)


GUM = '<script src="https://gumroad.com/js/gumroad.js"></script>'


def short(s, n=158):
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '…'


BANNER = """<div class="xmas-bar" id="xmasBar" hidden><span id="xmasText"></span><button type="button" aria-label="Close" onclick="document.getElementById('xmasBar').hidden=true;try{sessionStorage.setItem('xmasBarClosed','1')}catch(e){}">×</button></div>
<script>(function(){try{if(sessionStorage.getItem('xmasBarClosed'))return}catch(e){}
var n=new Date(),y=n.getFullYear(),t=new Date(n.getFullYear(),n.getMonth(),n.getDate()),x=new Date(y,11,25),d=Math.round((x-t)/864e5),el=document.getElementById('xmasText'),b=document.getElementById('xmasBar'),h='';
if(d<0||d>60)return;
if(d===0)h='🎄 Merry Christmas from Pip, Juniper and Waddles! <a href="/#free-pages">Grab a free coloring page</a>';
else if(n.getMonth()===11)h='🌟 Day <span class="num">'+n.getDate()+'</span> of the Christmas countdown: '+d+(d===1?' day':' days')+' to go! <a href="/cozy-christmas-countdown/">Get the Cozy Christmas Countdown</a>';
else h='🎄 Only <span class="num">'+d+'</span> days until Christmas! The 25-day countdown starts December 1st. <a href="/cozy-christmas-countdown/">See the Cozy Christmas Countdown</a>';
el.innerHTML=h;b.hidden=false;})();</script>
"""


def with_banner(html_text):
    return html_text.replace('<nav class="nav"', BANNER + '<nav class="nav"', 1)


ML_ACTION = "https://assets.mailerlite.com/jsonp/2770709/forms/203277074897568908/subscribe"
SIGNUP = f"""  <section class="section signup-band" id="signup" aria-labelledby="signup-h">
    <div class="wrap signup">
      <div class="signup-text">
        <span class="eyebrow">Snuggle Woods Story Club</span>
        <h2 id="signup-h">Free coloring pages in your inbox</h2>
        <p>Join free for new coloring pages, first news of new printables and holiday activities starring Pip, Juniper and Waddles. No spam, and you can unsubscribe anytime.</p>
      </div>
      <form class="signup-form" id="mlForm" action="{ML_ACTION}" method="post" novalidate>
        <label for="mlEmail" class="sr-only">Email address</label>
        <input id="mlEmail" type="email" name="fields[email]" placeholder="Your email address" autocomplete="email" required>
        <input type="hidden" name="ml-submit" value="1"><input type="hidden" name="anticsrf" value="true">
        <button class="btn berry" type="submit">Join free</button>
        <p class="signup-msg" id="mlMsg" role="status" aria-live="polite"></p>
      </form>
    </div>
  </section>
<script>(function(){{var f=document.getElementById('mlForm');if(!f)return;var m=document.getElementById('mlMsg'),b=f.querySelector('button');
f.addEventListener('submit',function(ev){{ev.preventDefault();var em=f.querySelector('input[type=email]');
if(!em.value||!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(em.value)){{m.textContent='Please enter a valid email address.';m.className='signup-msg err';em.focus();return}}
b.disabled=true;b.textContent='Joining…';m.textContent='';
fetch(f.action,{{method:'POST',body:new FormData(f)}}).then(function(r){{return r.json().catch(function(){{return {{}}}})}}).then(function(d){{
 if(d&&d.success===false)throw 0;f.reset();m.className='signup-msg ok';m.textContent='Almost done! Check your inbox and click the link to confirm your email. 💌';b.textContent='Joined ✓';}})
.catch(function(){{m.className='signup-msg err';m.textContent='Sorry, something went wrong. Please try again.';b.disabled=false;b.textContent='Join free';}});}});}})();</script>
"""


def free_pages_html():
    sm, wk = FREE['sample'], FREE['weekly']
    return f'''  <section class="section" id="free-pages" aria-labelledby="freepages-h">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">Free to print</span>
        <h2 id="freepages-h">Free coloring pages</h2>
        <p>Try a page from our Cozy Christmas Coloring Book before you buy. Every Sunday there's a new free page too.</p>
      </div>
      <div class="free-pages">
        <article class="free-card">
          <a href="/{sm['pdf']}" target="_blank" rel="noopener"><img src="/{sm['img']}" alt="Free sample coloring page: {e(sm['title'])}" width="600" height="776" loading="lazy"></a>
          <div class="body">
            <span class="tag on">Free sample</span>
            <h3>Page {sm['num']}: “{e(sm['title'])}”</h3>
            <p>The first page of our 50-page Christmas coloring story. Print it at home and see if your little one loves it.</p>
            <a class="btn berry" href="/{sm['pdf']}" target="_blank" rel="noopener">Download free PDF</a>
          </div>
        </article>
        <article class="free-card">
          <a href="/{wk['pdf']}" target="_blank" rel="noopener"><img src="/{wk['img']}" alt="Free coloring page of the week: {e(wk['title'])}" width="600" height="776" loading="lazy"></a>
          <div class="body">
            <span class="tag on">Page of the week</span>
            <h3>{e(wk['title'])}</h3>
            <p>{e(wk['caption'])} A new free page every Sunday, so come back next week!</p>
            <a class="btn berry" href="/{wk['pdf']}" target="_blank" rel="noopener">Download this week's page</a>
          </div>
        </article>
      </div>
      <p class="pp-note" style="margin-top:16px">Letter size (8.5 × 11 in). Crayons or colored pencils work best.</p>
    </div>
  </section>
''' + SIGNUP


def faq_html():
    items = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in FAQ)
    return f'''  <section class="section" id="faq" aria-labelledby="faq-h">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">Questions</span>
        <h2 id="faq-h">Frequently asked questions</h2>
      </div>
      <div class="faq">{items}</div>
    </div>
  </section>'''


def build_home():
    body = part('home_body.html').replace('{{KIDS_PRODUCTS}}', section_html('kids')).replace('{{PARENT_PRODUCTS}}', section_html('parents')).replace('{{FREE_PAGES}}', free_pages_html()).replace('{{FAQ}}', faq_html())
    desc = "Printable coloring and activity books for kids ages 3–8 starring Pip, Juniper and Waddles. Instant PDF downloads, plus printables for parents and our Cozy Christmas paperbacks."
    ld = [{"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": SITE + '/', "logo": SITE + '/apple-touch-icon.png',
           "sameAs": ["https://pin.it/1vTdeaMdw", "https://www.tiktok.com/@wonderkidz01", "https://www.instagram.com/wonderkidzstudio01/", "https://www.youtube.com/channel/UCoTcOowAHH3H11xoEOrQp6Q"]},
          {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + '/'},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": page_url(p), "name": p['title']} for i, p in enumerate(P)]}]
    h = head(f"{BRAND} | Printable Coloring & Activity Books for Kids 3–8", desc, SITE + '/', SITE + '/img/og-home.jpg', jsonld=ld)
    open(os.path.join(OUT, 'index.html'), 'w').write(h + with_banner(body).replace('</script>', '</script>', 1) + '\n' + GUM + '\n</body>\n</html>\n')


def build_product(p):
    sec_name, sec_anchor = ('For parents', 'parents') if p['section'] == 'parents' else ('Kids printables', 'shop')
    price = p['price'].lstrip('$')
    desc = short(f"{p['desc']} Instant PDF download from {BRAND}.")
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p['title'], "image": [f"{SITE}/{p['img']}"], "description": p['desc'],
          "brand": {"@type": "Brand", "name": BRAND}, "sku": p['slug'],
          "offers": {"@type": "Offer", "url": page_url(p), "priceCurrency": "USD", "price": price, "availability": "https://schema.org/InStock"}}
    meta = (f'<meta property="product:price:amount" content="{price}">\n<meta property="product:price:currency" content="USD">\n'
            f'<meta property="og:price:amount" content="{price}">\n<meta property="og:price:currency" content="USD">\n'
            f'<meta property="product:availability" content="instock">\n<meta property="og:availability" content="instock">')
    h = head(f"{p['title']} | {BRAND}", desc, page_url(p), f"{SITE}/{p['img']}", 'product', meta, ld)
    was = f'<span class="was">{e(p["was"])}</span>' if p.get('was') else ''
    badge = f' <span class="save-badge">{e(p["badge"])}</span>' if p.get('badge') else ''
    incl = ''
    if p.get('includes'):
        incl = '<div class="pp-incl"><h2>What\'s included</h2>' + ''.join(
            f'<a href="/{s}/"><img src="/img/{s}-480.jpg" alt="" width="56" height="56">{e(BY[s]["title"])}</a>' for s in p['includes']) + '</div>'
    others = [o for o in P if o['slug'] != p['slug'] and o['section'] == p['section'] and not o.get('featured')]
    if p['section'] == 'parents' or len(others) < 3:
        others += [o for o in P if o['slug'] != p['slug'] and o not in others and not o.get('featured')]
    more = ''.join(card(o) for o in others[:3])
    bundle_tip = ''
    b = BY.get('ultimate-christmas-activity-bundle')
    if b and p['slug'] in b.get('includes', []):
        bundle_tip = f'<p class="pp-note">💡 Also in the <a href="/{b["slug"]}/">{e(b["title"])}</a>: all three Cozy Christmas printables for {e(b["price"])}.</p>'
    lis = ''.join(f'<li>{e(x)}</li>' for x in p['bullets'])
    body = f'''{SPRITE}
{rel_nav(NAV)}
<main>
<section class="section pp-section">
  <div class="wrap">
    <p class="crumbs"><a href="/">Home</a> › <a href="/#{sec_anchor}">{sec_name}</a> › {e(p['title'])}</p>
    <div class="pp">
      <div class="pp-cover cover-wrap"><img src="/{p['img']}" alt="{e(p['alt'])}" width="1000" height="1000">
        <a class="pin-btn" href="{e(pin_link(p))}" target="_blank" rel="noopener" aria-label="Save to Pinterest">{PIN_SVG}Save</a></div>
      <div class="pp-info">
        <span class="tag on">{e(p['tag'])}</span>
        <h1>{e(p['title'])}{badge}</h1>
        <p class="pp-price">{e(p['price'])}{was}</p>
        <p class="lead">{e(p['desc'])}</p>
        <ul>{lis}</ul>
        <div class="pp-buy">{buy_btn(p, True)}<span class="where">Secure checkout by Gumroad</span></div>
        <p class="pp-note">Instant PDF download. Print at home, as many copies as your family needs.</p>
        {bundle_tip}
        {incl}
      </div>
    </div>
    <div class="pp-more">
      <h2>More printables you might like</h2>
      <div class="product-grid">{more}</div>
      <p><a class="btn plain" href="/#{sec_anchor}">See all printables</a></p>
    </div>
  </div>
</section>
</main>
{rel_nav(FOOTER)}
{GUM}
</body>
</html>
'''
    d = os.path.join(OUT, p['slug']); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(h + with_banner(body))


def build_404():
    h = head(f"Page not found | {BRAND}", "This page wandered off into Snuggle Woods. Head back to our printables.", SITE + '/404.html', SITE + '/img/og-home.jpg')
    body = f'''{SPRITE}
{rel_nav(NAV)}
<main class="nf"><div>
  <svg class="pip" aria-hidden="true"><use href="#pip"/></svg>
  <h1>Oops! This page wandered off into Snuggle Woods.</h1>
  <p>Pip looked everywhere, but couldn't find it. Let's get you back to the fun stuff.</p>
  <p style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:22px"><a class="btn berry" href="/#shop">See the printables</a><a class="btn plain" href="/#free">Get free printables</a></p>
</div></main>
{rel_nav(FOOTER)}
</body>
</html>
'''
    open(os.path.join(OUT, '404.html'), 'w').write(with_banner(h.replace('<meta name="theme-color"', '<meta name="robots" content="noindex">\n<meta name="theme-color"') + body))


def build_meta_files():
    urls = [SITE + '/'] + [page_url(p) for p in P]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    sm += f'  <url><loc>{SITE}/</loc><lastmod>{TODAY}</lastmod><priority>1.0</priority><image:image><image:loc>{SITE}/img/og-home.jpg</image:loc></image:image></url>\n'
    for p in P:
        sm += f'  <url><loc>{page_url(p)}</loc><lastmod>{TODAY}</lastmod><priority>0.8</priority><image:image><image:loc>{SITE}/{p["img"]}</image:loc></image:image></url>\n'
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(sm + '</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')


def ensure_thumbs():
    for p in P:
        src = os.path.join(OUT, p['img']); th = os.path.join(OUT, 'img', p['slug'] + '-480.jpg')
        if not os.path.exists(th):
            im = Image.open(src).convert('RGB'); im.thumbnail((480, 480)); im.save(th, quality=80, optimize=True, progressive=True)


if __name__ == '__main__':
    ensure_thumbs(); build_home()
    for p in P: build_product(p)
    build_404(); build_meta_files()
    print('built', 1 + len(P) + 1, 'pages')
