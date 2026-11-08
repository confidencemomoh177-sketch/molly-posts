# Wonder Kidz Studio — weekly autopilot runbook

Each Sunday's scheduled run follows this file from top to bottom. It builds and schedules the next **Monday–Sunday** week: 3 slots a day × 4 platforms = 84 posts. It then sends Charlize a report.

## Fixed settings
- Metricool brand "Wonder Kidz Studio", blogId **7850012**. Networks: TikTok, Instagram (REEL), YouTube (short), Pinterest.
- Pinterest boardId **1140888586794329019** (board "Christmas Activities for Kids").
- Slots: **09:00, 13:00, 20:00 America/New_York**.
- Every post links to the website: `https://wonderkidzstudio.pages.dev`. The short link `https://tinyurl.com/wonderkidz01` goes to the same site.
  - Captions say "link in bio".
  - YouTube descriptions and the pinned comment use the short link.
  - The Pinterest pinLink is the matching **product page**, not the homepage: coloring pins → `/cozy-christmas-coloring-book-printable/`, activity pins → `/cozy-christmas-activity-book-printable/`, countdown/advent hooks → `/cozy-christmas-countdown/`, gift/bundle hooks → `/ultimate-christmas-activity-bundle/` (all on `https://wonderkidzstudio.pages.dev`). Exception: a pin whose text promises the free printables ("34 more … free") links to the homepage, where the free download is. No tracking parameters needed.
  - **Gumroad links never go in posts.** They go on the website only.
- Cloudinary cloud `u8nockph`. Upload by remote URL from `raw.githubusercontent.com/confidencemomoh177-sketch/molly-posts/<commit SHA>/...`, because the shell can't reach Cloudinary.

## Rules (from the project)
- Never mention any author name. The brand is "Wonder Kidz Studio".
- Use only facts stated in the books (`assets/books/coloring.txt`, `activity.txt`) or on the store page.
- Match every photo to its page by **looking at it**, never by page number alone.
- Music comes only from `make_music.py` tracks (in `assets/music`). No trending sounds. TikTok `autoAddMusic` false.
- Switch on the AI label everywhere:
  - TikTok `isAigc: true`
  - Instagram `isAiGenerated: true`
  - YouTube `isAiGeneratedContent: true`, `madeForKids: false`, category EDUCATION
  - Pinterest `isAiGenerated: true`
- TikTok needs `tiktokData.title` (use the hook).
- Coloring posts must never claim that a child colored the page.

## Steps
1. **Restore the workspace.**
   - Attach the repo with push access and clone it to `/home/claude/molly-posts`.
   - Run `bash wonder-kidz-studio/setup.sh`.
   - `pip install python-docx --break-system-packages` if it's needed.
2. **Read the state.**
   - `state/posted.json` and `state/calendar.json` show what has been posted.
   - `assets/books/items.json` is the inventory of all 123 activity and coloring pages.
   - `colored_pages/status.json` shows which colored pages are `ready` and which are `used`.
3. **Plan 21 posts.**
   - Every coloring page with status `ready` becomes a **coloring-transformation post**. Use `state/color_post.py`; its item keys are in `assets/work/item_*.json` from earlier coloring posts.
   - Fill the remaining slots with **activity pages not used before**, using the `A` template in `state/items.py` and `state/build.py`.
   - Never repeat a page that has already been posted.
   - Alternate coloring and activity posts. Put the strongest gift and countdown hooks in the 20:00 slots and at the weekend.
   - Mid-December onward: lean on countdown, Christmas Eve and last-minute-gift angles.
4. **Write the items.**
   - Write a new `state/items_weekN.py`, or extend `ITEMS`, using the same fields as week 1: `tt`, `ig`, `tags`, `yt`, `ytd`, `pt`, `pd`, `pin_title`/`pin_sub`, hook and `sub`.
   - For coloring posts: `hook`, `sub` = "Page N of 50 · swipe to watch it fill in", `half_title` "Halfway there…", `full_title` "All colored in!", `full_sub` "+ 34 free printables inside".
5. **Build.**
   - Activity posts: `python3 state/build.py <keys>`.
   - Coloring posts: `python3 state/color_post.py item.json`.
   - Make a contact sheet of every post's slides and the pin, then **open it and check it**: right picture, no clipped text, no author name.
6. **Publish.**
   - Copy each `video.mp4` and `pin.jpg` (converted from PNG) to `posts_wN/NN_key/`.
   - Commit and push, then upload each file to Cloudinary from its raw GitHub URL pinned to the commit SHA.
7. **Schedule.**
   - Create one Metricool post per platform for each post, 84 in total. `state/mc.py` shows the JSON shape.
   - Check with `getScheduledPosts` across the week: 84 posts, none missing, no duplicates.
8. **Next ChatGPT round.**
   - Pick the next 6–7 unused coloring pages. In the coloring PDF, page N of 50 = PDF page `2N+7`.
   - Render them at 200 dpi and crop `(120,110,1580,1830)`.
   - Build the Word file with `assets/work/chatgpt_doc_template.js`, which already has the prompt, the character colors and the reference image.
   - Send the file to Charlize. When she uploads ChatGPT's file back, a live session extracts the images, adds them to `colored_pages/` and marks them `ready`.
9. **Update the state and report.**
   - Update `posted.json`, `calendar.json` and `colored_pages/status.json` (newly used pages become `used`), then commit.
   - Send Charlize a short report:
     - what was scheduled each day;
     - a slides contact sheet;
     - the ChatGPT Word file;
     - Metricool analytics for last week's posts, if available (top posts by views or saves);
     - **a ready-to-send newsletter** (subject, preview text, body) for the MailerLite "Website sign-ups" group: this week's new free coloring page (link `https://wonderkidzstudio.pages.dev/free/free-coloring-page-of-the-week.pdf`) plus ONE product with its product-page link (rotate: bundle → Countdown → coloring → activity). Warm, short, no author names, no Gumroad links (link product pages on the site). She pastes it into MailerLite and sends it herself;
     - anything she needs to do.
   - If a step fails, still send the report and say exactly what failed.

## Website hosting
- Live site: https://wonderkidzstudio.pages.dev (Cloudflare Pages project "wonderkidzstudio", account handelglobalgm@gmail.com; auto-deploys from `main`, output dir `wonder-kidz-studio/site`, no build command). Moved from Netlify on 2026-11-08 because Netlify free credits ran out; the old address wonderkidzstudio.netlify.app still serves the Nov 5 version and will redirect here once Netlify deploys again (credits reset Dec 4; redirect is in /netlify.toml).
- The site is GENERATED: edit `site_src/` (products.json for products, home_body.html for homepage text, head_styles.html for styles), then run `python3 site_src/build_site.py`, commit and push to `main`; Cloudflare Pages publishes within about a minute. Never hand-edit files in `site/` except images in `site/img/`.
- New product: add a square ~1000px cover as `site/img/<slug>.jpg` and an entry in `site_src/products.json`; the build makes its card, its own page at /<slug>/, the sitemap entry and Pinterest/Google tags.
- Product pages can be used as Pinterest pin links (e.g. https://wonderkidzstudio.pages.dev/cozy-christmas-countdown/).

## Weekly free coloring page (website)
Every Sunday run, after scheduling: pick a coloring page (1–50) that is NOT in `site_src/free_pages.json` (sample, weekly or history) and preferably not one being posted this week, then run
`python3 site_src/rotate_free_page.py <num> "<Short title>"` and `python3 site_src/build_site.py`, look at `site/img/free-coloring-page-of-the-week.jpg`, commit and push. Mention the new free page in the report.
Never give away more than one page a week; the sample page (page 1) stays fixed.

## Email list (MailerLite)
- The site's green "Snuggle Woods Story Club" section (#signup) posts to MailerLite form 203277074897568908 (account 2770709). Double opt-in is on.
- Confirmed sign-ups join the group "Website sign-ups (free coloring page)". The automation "Welcome – free coloring page" then sends the welcome email with both free PDFs.
- The welcome email links to the stable PDF URLs, so the weekly free-page rotation needs no MailerLite change. Don't touch the form or the automation unless Charlize asks.
