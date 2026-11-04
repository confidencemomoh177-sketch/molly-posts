const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, ImageRun, AlignmentType, PageBreak, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, LevelFormat, HeadingLevel, Footer, PageNumber, VerticalAlign, HeightRule } = require('docx');
const { STYLE, DAYS, BINGO, WORDS } = require('./content');

const RED = 'C62033', GREEN = '1C4A33', GOLD = 'B8860B', INK = '1F2433', SOFT = '5A5F6E';
const W = 10080; // content width in DXA (8.5in - 2*0.6in margins... see section)
const T = (text, o = {}) => new TextRun({ text, font: 'Arial', ...o });
const P = (runs, o = {}) => new Paragraph({ spacing: { after: 120, line: 300 }, ...o, children: Array.isArray(runs) ? runs : [T(runs)] });
const C = (runs, o = {}) => P(runs, { alignment: AlignmentType.CENTER, ...o });
const br = () => new Paragraph({ children: [new PageBreak()] });
const H1 = (t, color = GREEN) => new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, children: [T(t, { color })] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [T(t)] });
const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noB = { top: none, bottom: none, left: none, right: none };
const line = { style: BorderStyle.SINGLE, size: 6, color: '9A9A9A' };

// The box ChatGPT replaces with a picture
function imgBox(prompt, h = 4200, label = 'IMAGE PROMPT') {
  const b = { style: BorderStyle.DASHED, size: 12, color: GOLD };
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: [new TableRow({
    height: { value: h, rule: HeightRule.ATLEAST },
    children: [new TableCell({ width: { size: W, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      borders: { top: b, bottom: b, left: b, right: b }, shading: { fill: 'FFF8E6', type: ShadingType.CLEAR, color: 'auto' },
      margins: { top: 160, bottom: 160, left: 220, right: 220 },
      children: [C([T(`🖼 ${label} (replace this box with the picture)`, { bold: true, color: GOLD, size: 20 })]),
                 C([T(prompt, { italics: true, color: SOFT, size: 20 })], { spacing: { after: 0 } })] })] })] });
}
function writeLines(n, label) {
  const out = [];
  if (label) out.push(P([T(label, { bold: true, size: 26 })], { spacing: { before: 160, after: 80 } }));
  out.push(new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: Array.from({ length: n }, () => new TableRow({ height: { value: 620, rule: HeightRule.EXACT },
    children: [new TableCell({ width: { size: W, type: WidthType.DXA }, borders: { top: none, left: none, right: none, bottom: line }, children: [P(' ')] })] })) }));
  return out;
}
function drawBox(label, h = 5200) {
  const b = { style: BorderStyle.SINGLE, size: 12, color: INK };
  return [P([T(label, { bold: true, size: 26 })], { spacing: { before: 120, after: 80 } }),
    new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: [new TableRow({ height: { value: h, rule: HeightRule.EXACT },
      children: [new TableCell({ width: { size: W, type: WidthType.DXA }, borders: { top: b, bottom: b, left: b, right: b }, children: [P(' ')] })] })] })];
}
function grid(cols, rows, cellFn, h = 900, fs = 28) {
  const cw = Math.floor(W / cols); const b = { style: BorderStyle.SINGLE, size: 10, color: INK };
  return new Table({ width: { size: cw * cols, type: WidthType.DXA }, columnWidths: Array(cols).fill(cw), alignment: AlignmentType.CENTER,
    rows: Array.from({ length: rows }, (_, r) => new TableRow({ height: { value: h, rule: HeightRule.ATLEAST },
      children: Array.from({ length: cols }, (_, c) => { const v = cellFn(r, c);
        return new TableCell({ width: { size: cw, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER, borders: { top: b, bottom: b, left: b, right: b },
          shading: v.fill ? { fill: v.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined, margins: { top: 60, bottom: 60, left: 80, right: 80 },
          children: (Array.isArray(v.t) ? v.t : [v.t]).map((t, i) => C([T(t, { size: i ? Math.round(fs * 0.62) : fs, bold: !i && v.bold !== false, color: v.color || INK })], { spacing: { after: 0 } })) }); }) })) });
}
function list(items, ref = 'num') { return items.map(s => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 100, line: 300 }, children: [T(s, { size: 26 })] })); }

// ---------- word search (deterministic, across & down only) ----------
function wordSearch() {
  const N = 9, g = Array.from({ length: N }, () => Array(N).fill(''));
  const place = [['STAR', 0, 0, 'a'], ['CARD', 0, 5, 'a'], ['TREE', 1, 7, 'd'], ['SNOW', 2, 1, 'a'], ['COCOA', 3, 0, 'd'], ['GIFT', 5, 2, 'a'], ['BELL', 7, 3, 'a'], ['SCARF', 8, 4, 'a']];
  const sol = new Set();
  for (const [w, r, c, d] of place) [...w].forEach((ch, i) => { const rr = d === 'd' ? r + i : r, cc = d === 'a' ? c + i : c;
    if (g[rr][cc] && g[rr][cc] !== ch) throw new Error('clash ' + w); g[rr][cc] = ch; sol.add(rr + ',' + cc); });
  const fill = 'HOLLYJINGLEMERRYPEACEJOYWREATHMITTENELFSLEDCANDY'; let k = 0;
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (!g[r][c]) g[r][c] = fill[(k++ * 7) % fill.length];
  return { g, sol, N };
}
const WS = wordSearch();

// ---------- pages ----------
const kids = [];
// 0. ChatGPT instructions (to delete)
kids.push(H1('Instructions for ChatGPT', RED),
  P([T('Please read before starting. Delete this page from the finished book.', { italics: true, color: RED })], { alignment: AlignmentType.CENTER }),
  H2('What to do'),
  ...list(['This document is a complete printable children\'s book. Every gold dashed box marked "IMAGE PROMPT" needs one picture.',
    'For each box, generate the picture described in the prompt and put it in place of the box, same size or as large as fits the page. Keep all text exactly as written.',
    'Work in order from the front cover to the last page. Keep the characters looking the same in every picture.',
    'When finished, give back ONE Word document (.docx) with all pictures embedded and this instructions page removed.']),
  H2('Style for the inside pictures'), P([T(STYLE, { size: 24 })]),
  H2('The characters (always draw them like this)'),
  ...list(['Pip: a round, cuddly brown bear cub, rosy cheeks, always wearing a red-and-white striped scarf. Loves cocoa, cookies and hugs.',
    'Juniper: a cream-colored bunny with long floppy ears and a knitted hat with a big pom-pom. Loves making crafts.',
    'Waddles: a small, round navy-and-white penguin with orange beak and feet, wearing fluffy earmuffs. Loves snow.',
    'Grandma Owl: a kind old owl with round glasses and a knitted shawl.',
    'The golden star: a small, simple five-point star. It appears once in each day\'s picture.'], 'dot'),
  P([T('Only the front cover is in full color. Every inside picture is black-and-white line art that children can color.', { bold: true })]),
  br());
// 1. Cover
kids.push(imgBox('FRONT COVER, full color, portrait 8.5 × 11. Bright, cozy, high-quality children\'s book cover. Snowy Snuggle Woods at dusk with a cozy cottage and twinkling lights. Pip the bear, Juniper the bunny and Waddles the penguin (see character notes) smiling around a glowing glass lantern filled with little golden stars, with a paper chain and an open advent calendar with numbered doors nearby. Title text at the top, spelled exactly: "Cozy Christmas Countdown". Subtitle in a ribbon banner: "A 25-Day Advent Activity Calendar for Kids". A round badge: "25 Days of Stories, Crafts & Kindness". Small text: "Ages 4–8". Bottom banner: "Wonder Kidz Studio". Same art style as the Cozy Christmas Coloring Book cover. Also make a square version for the online shop.', 12600, 'FRONT COVER IMAGE PROMPT'), br());
// 2. Title
kids.push(new Paragraph({ spacing: { before: 2400 }, children: [] }), H1('Cozy Christmas Countdown', RED),
  C([T('A 25-Day Advent Activity Calendar for Kids', { size: 32, color: GREEN, bold: true })]),
  C([T('A Snuggle Woods Christmas Story with Pip, Juniper & Waddles', { size: 26, italics: true, color: SOFT })], { spacing: { after: 600 } }),
  imgBox('Small title-page picture: the empty glass lantern sitting on a snowy windowsill with one tiny five-point star beside it. Simple, centered.', 3600),
  C([T('Wonder Kidz Studio', { size: 30, bold: true, color: GREEN })], { spacing: { before: 600 } }), br());
// 3. Copyright
kids.push(new Paragraph({ spacing: { before: 6000 }, children: [] }),
  C([T('Cozy Christmas Countdown: A 25-Day Advent Activity Calendar for Kids', { bold: true })]),
  C('Copyright © 2026 Wonder Kidz Studio. All rights reserved.'),
  C('This printable book is for personal, non-commercial use. You may print as many copies as your own household or classroom needs. Please do not share, resell or upload the file.'),
  C('Pip, Juniper, Waddles, Grandma Owl and Snuggle Woods are original characters created by Wonder Kidz Studio.'),
  C([T('Grown-ups: some activities use scissors, tape or the kitchen. Please help and supervise little ones.', { italics: true, color: SOFT })]), br());
// 4. Belongs to
kids.push(new Paragraph({ spacing: { before: 1200 }, children: [] }), H1('This Book Belongs To'), ...writeLines(1),
  new Paragraph({ spacing: { after: 600 }, children: [] }),
  imgBox('Pip, Juniper and Waddles waving hello, standing together in the snow, holding a big blank sign (no letters on the sign). Black-and-white line art for coloring.', 6200), br());
// 5. How to use
kids.push(H1('Hello, Christmas Counter!'),
  P([T('Grandma Owl has given Pip, Juniper and Waddles a magic lantern. Every day in December, one golden star appears somewhere in Snuggle Woods. Can you help the friends find all 25 stars before Christmas?', { size: 26 })]),
  H2('How it works'),
  ...list(['Every day from December 1st to 25th, turn to that day\'s pages.', 'Read the story together and color the picture. Can you spot the golden star?', 'Do the day\'s activity on the next page.', 'Do the Kindness Mission. Kindness is the most important star of all!', 'Color that day\'s star on your Star Tracker.']),
  H2('Grown-ups'), P([T('Print one day at a time, or the whole book at once. Each day has a short story to read aloud, a picture to color, an activity and a small kindness mission. Most days take 15–30 minutes. Answers are at the back.', { size: 24 })]),
  H2('What you\'ll need'),
  ...list(['Crayons, colored pencils or markers', 'Pencil and eraser', 'Child-safe scissors (with a grown-up)', 'Glue stick and tape', 'Some scrap paper and string'], 'dot'), br());
// 6. Meet the friends
kids.push(H1('Meet the Snuggle Woods Friends'),
  imgBox('Pip the bear cub, Juniper the bunny and Waddles the penguin standing side by side in a row, each full-body and smiling, with plenty of space around them. Black-and-white line art for coloring.', 4600),
  P([T('Pip ', { bold: true, color: RED, size: 28 }), T('the bear cub loves hot cocoa, warm cookies and big hugs. He never goes anywhere without his striped scarf.', { size: 26 })], { spacing: { before: 240 } }),
  P([T('Juniper ', { bold: true, color: RED, size: 28 }), T('the bunny loves making things: paper chains, ornaments and cards. Her pom-pom hat bounces when she hops!', { size: 26 })]),
  P([T('Waddles ', { bold: true, color: RED, size: 28 }), T('the penguin loves snow more than anything. Sledding, snowballs, snowmen… he\'s the first one outside every morning.', { size: 26 })]),
  P([T('Grandma Owl ', { bold: true, color: RED, size: 28 }), T('is the wisest owl in Snuggle Woods, and she has a very special lantern…', { size: 26 })]), br());
// 7. Star tracker
kids.push(H1('My Star Tracker'), C([T('Color one star each day after you finish. When all 25 are colored, the lantern is full!', { size: 26 })], { spacing: { after: 300 } }),
  grid(5, 5, (r, c) => ({ t: ['☆', `Dec ${r * 5 + c + 1}`], bold: false }), 1900, 72), br());

// ---------- the 25 days ----------
DAYS.forEach((d, i) => {
  const n = i + 1;
  // Story page
  kids.push(new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: [new TableRow({ children: [new TableCell({
      width: { size: W, type: WidthType.DXA }, borders: noB, shading: { fill: RED, type: ShadingType.CLEAR, color: 'auto' }, margins: { top: 100, bottom: 100, left: 200, right: 200 },
      children: [C([T(`DAY ${n}  ·  DECEMBER ${n}`, { bold: true, color: 'FFFFFF', size: 26 })], { spacing: { after: 0 } })] })] })] }),
    H1(d.t),
    imgBox(d.img + ' Black-and-white line art for coloring.', 6600),
    ...d.story.map(s => P([T(s, { size: 27 })], { spacing: { before: 120, after: 100, line: 320 } })),
    new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: [new TableRow({ children: [new TableCell({
      width: { size: W, type: WidthType.DXA }, borders: { top: { style: BorderStyle.SINGLE, size: 12, color: GREEN }, bottom: { style: BorderStyle.SINGLE, size: 12, color: GREEN }, left: { style: BorderStyle.SINGLE, size: 12, color: GREEN }, right: { style: BorderStyle.SINGLE, size: 12, color: GREEN } },
      shading: { fill: 'EEF6F1', type: ShadingType.CLEAR, color: 'auto' }, margins: { top: 120, bottom: 120, left: 200, right: 200 },
      children: [P([T('💚 Kindness Mission: ', { bold: true, color: GREEN, size: 26 }), T(d.kind, { size: 26 })], { spacing: { after: 60 } }),
                 P([T(`☐  I found star #${n}!   ☐  I did my Kindness Mission!`, { bold: true, size: 24 })], { spacing: { after: 0 } })] })] })] }),
    br());
  // Activity page
  const a = d.act;
  kids.push(C([T(`DAY ${n} ACTIVITY`, { bold: true, color: RED, size: 24 })], { spacing: { after: 0 } }), H1(a.h));
  if (a.steps) kids.push(...list(a.steps, `n${n}`));
  if (a.img) kids.push(imgBox(a.img + ' Black-and-white line art, thick outlines, white background.', a.steps ? 5400 : 8600));
  if (a.kind === 'chain') kids.push(P([T('Tip: the paper chain strips are near the back of the book.', { italics: true, color: SOFT, size: 24 })]), ...drawBox('Draw what you hope to find this Christmas', 4600));
  if (a.kind === 'snowballs') kids.push(new Paragraph({ spacing: { before: 200 }, children: [] }), grid(5, 2, () => ({ t: '◯' }), 1500, 64),
    P([T('How many did you get in? ', { bold: true, size: 26 }), T('_______ out of 10', { size: 26 })], { spacing: { before: 300 } }));
  if (a.wordsearch) kids.push(grid(WS.N, WS.N, (r, c) => ({ t: WS.g[r][c] }), 820, 34),
    C([T('Find: ' + WORDS.join('  •  '), { bold: true, size: 26 })], { spacing: { before: 240 } }));
  if (a.bingo) kids.push(grid(3, 3, (r, c) => ({ t: BINGO[r * 3 + c], fill: (r + c) % 2 ? 'FFFFFF' : 'FFF3F4' }), 2500, 26));
  if (a.moves) kids.push(grid(3, a.moves.length, (r, c) => c === 0 ? { t: a.moves[r][0] } : c === 1 ? { t: a.moves[r][1], bold: false } : { t: '☆', bold: false }, 1200, 26));
  if (a.spy) kids.push(grid(2, 4, (r, c) => ({ t: '☐  ' + a.spy[r * 2 + c], bold: false }), 1500, 28));
  if (a.jokes) a.jokes.forEach(([q, ans]) => kids.push(P([T('Q: ' + q, { bold: true, size: 27 })], { spacing: { before: 200, after: 40 } }), P([T('A: ' + ans, { size: 27, color: RED })])));
  if (a.rhythm) kids.push(grid(4, 4, (r, c) => r < 3 ? ({ t: [['CLAP', 'CLAP', 'PAT', 'PAT'], ['CLAP', 'PAT', 'CLAP', 'PAT'], ['PAT', 'PAT', 'PAT', 'CLAP']][r][c], fill: [['FFF3F4', 'FFF3F4', 'EEF6F1', 'EEF6F1'], ['FFF3F4', 'EEF6F1', 'FFF3F4', 'EEF6F1'], ['EEF6F1', 'EEF6F1', 'EEF6F1', 'FFF3F4']][r][c] }) : ({ t: '?', color: SOFT }), 1500, 30),
    P([T('CLAP = clap your hands   •   PAT = pat your knees', { size: 24, color: SOFT })], { alignment: AlignmentType.CENTER, spacing: { before: 200 } }));
  if (a.scramble) kids.push(grid(2, a.scramble.length, (r, c) => c === 0 ? { t: a.scramble[r][0] } : { t: '_ '.repeat(a.scramble[r][1].length).trim(), bold: false, color: SOFT }, 1100, 34));
  if (a.box && !a.lines) kids.push(...drawBox(a.box, 8200));
  if (a.box && a.lines) kids.push(...drawBox(a.box, a.lines > 1 ? 5600 : 7600));
  if (a.lines) kids.push(...writeLines(a.lines, a.linesLabel));
  if (a.note) kids.push(P([T(a.note, { italics: true, color: SOFT, size: 24 })], { spacing: { before: 200 } }));
  kids.push(br());
});

// ---------- back matter ----------
// Paper chain strips
kids.push(H1('Countdown Paper Chain Strips'), C([T('Color, cut along the lines, and link them together (see Day 1). Tear one off every morning!', { size: 24 })], { spacing: { after: 200 } }),
  grid(2, 13, (r, c) => { const n = r * 2 + c + 1; return n > 25 ? { t: '★ Merry Christmas! ★', color: RED } : { t: `★  ${n}  ★   ${25 - n === 0 ? 'Christmas Day!' : (25 - n) + (25 - n === 1 ? ' day to go' : ' days to go')}`, bold: false }; }, 830, 26), br());
// Answer key
kids.push(H1('Answer Key'), H2('Day 6: Christmas word search'),
  grid(WS.N, WS.N, (r, c) => WS.sol.has(r + ',' + c) ? { t: WS.g[r][c], fill: 'FFE58A' } : { t: WS.g[r][c], color: 'BBBBBB', bold: false }, 560, 24),
  H2('Day 19: Unscramble the snowy words'), P([T(DAYS[18].act.scramble.map(([s, w]) => `${s} = ${w}`).join('   •   '), { size: 26 })]), br());
// Certificate
const cb = { style: BorderStyle.DOUBLE, size: 24, color: RED };
kids.push(new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: [new TableRow({ height: { value: 13000, rule: HeightRule.ATLEAST }, children: [new TableCell({
  width: { size: W, type: WidthType.DXA }, borders: { top: cb, bottom: cb, left: cb, right: cb }, margins: { top: 400, bottom: 400, left: 400, right: 400 }, verticalAlign: VerticalAlign.CENTER,
  children: [H1('Certificate', RED), C([T('Christmas Countdown Champion', { bold: true, size: 36, color: GREEN })], { spacing: { after: 300 } }),
    C([T('This certifies that', { size: 26 })]), ...writeLines(1), C([T('found all 25 golden stars, finished the Cozy Christmas Countdown and filled Snuggle Woods with kindness!', { size: 26 })], { spacing: { before: 300 } }),
    imgBox('Pip, Juniper and Waddles cheering and holding up the glowing lantern full of stars, with confetti stars around them. Black-and-white line art for coloring.', 3800),
    P([T('Date: ______________________        Signed: ______________________', { size: 24 })], { alignment: AlignmentType.CENTER, spacing: { before: 400 } })] })] })] }), br());
// Last page – QR
kids.push(new Paragraph({ spacing: { before: 800 }, children: [] }), H1('Thank You from Snuggle Woods!', RED),
  C([T('We hope your family had the coziest Christmas countdown.', { size: 28 })]),
  C([T('Want more coloring pages, activity books and free printables starring Pip, Juniper and Waddles?', { size: 28 })], { spacing: { after: 400 } }),
  C([T('Scan to visit our website', { bold: true, size: 32, color: GREEN })]),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 200 }, children: [new ImageRun({ type: 'png', data: fs.readFileSync('qr.png'), transformation: { width: 230, height: 230 }, altText: { title: 'QR code', description: 'QR code to the Wonder Kidz Studio website', name: 'qr' } })] }),
  C([T('tinyurl.com/wonderkidz01', { bold: true, size: 28 })]),
  C([T('Grown-ups: if your family enjoyed this book, a short review helps other families find us. Thank you!', { italics: true, size: 24, color: SOFT })], { spacing: { before: 400 } }),
  C([T('Merry Christmas from all of us at Wonder Kidz Studio!', { bold: true, size: 30, color: RED })], { spacing: { before: 500 } }));

const numRefs = ['num', ...DAYS.map((_, i) => `n${i + 1}`)].map(reference => ({ reference, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 360 } } } }] }));
const doc = new Document({
  creator: 'Wonder Kidz Studio', title: 'Cozy Christmas Countdown: A 25-Day Advent Activity Calendar for Kids', description: 'Wonder Kidz Studio',
  numbering: { config: [...numRefs, { reference: 'dot', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 360 } } } }] }] },
  styles: { default: { document: { run: { font: 'Arial', size: 24, color: INK } },
    heading1: { run: { font: 'Arial', size: 48, bold: true, color: GREEN }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 120, after: 200 }, keepNext: true } },
    heading2: { run: { font: 'Arial', size: 30, bold: true, color: RED }, paragraph: { spacing: { before: 240, after: 100 }, keepNext: true } } } },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1000, bottom: 1000, left: 1080, right: 1080, footer: 500 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [T('Cozy Christmas Countdown  ·  Wonder Kidz Studio  ·  ', { size: 16, color: '999999' }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: '999999', font: 'Arial' })] })] }) },
    children: kids }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync('Cozy Christmas Countdown - for ChatGPT.docx', b); console.log('written'); });
