import json, sys, datetime
sys.path.insert(0,'.')
from items_w4 import ITEMS, ORDER
from captions_w4 import C
FULL, SHORT, WK = sys.argv[1], sys.argv[2], sys.argv[3]   # WK = dir with items_{key}.json
start=datetime.date(2026,11,24); times=["09:00","13:00","19:00"]
cal=json.load(open('calendar.json')); base=len(cal); tracks={}
assert base==63
for n,key in enumerate(ORDER):
    it=next(i for i in ITEMS if i['key']==key); c=C[key]
    item=json.load(open(f'{WK}/items_{key}.json'))
    day=start+datetime.timedelta(days=n//3); t=times[n%3]
    tt=f"{it['hook']} ✨ {c['tt']} {c['q']}\nFull guide in bio. " + " ".join(c['tags']+["#christmasmarkets","#europetravel"])
    ig=f"{it['hook']}.\n\n{c['ig']}\n\n{c["q"]}\n\nSave this for your trip planning 🎄\nDates, hours & itineraries for every market are in the guide (link in bio).\n\n" + " ".join(c['tags']+["#christmasmarkets","#europeanchristmasmarkets","#christmasineurope","#europetravel","#wintertravel"])
    ytt=(c['yt']+" #shorts")
    ytd=f"{c['ytd']} {c['q']}\nGet the European Christmas Markets Guide 2026–2027: {SHORT}\n#christmasmarkets #europetravel #shorts"
    row=dict(n=base+n+1,key=key,date=str(day),time=t,timezone="America/New_York",hook_type=it['hook_type'],hook=it['hook'],
             music=item['music'].split('/')[-1],out=f"posts/{base+n+1}_{key}",tiktok=tt,instagram=ig,youtube_title=ytt,youtube_desc=ytd,
             youtube_pinned_comment=f"📖 The full guide: {SHORT}",pin_title=c['pt'],pin_desc=c['pd'],pin_link=FULL,
             instagram_format="reel",status="draft")
    cal.append(row)
    assert len(ytt)<=60, ytt; assert len(c['pt'])<100, c['pt']; assert len(c['pd'])<500, key; assert len(tt)<2200
    tracks[row['music']]=tracks.get(row['music'],0)+1
json.dump(cal,open('calendar.json','w'),indent=1,ensure_ascii=False)
print('rows',len(cal),'max track uses', max(tracks.values()))
w=cal[base:]
for a,b in zip(w,w[1:]):
    if a['hook_type']==b['hook_type']: print('same hook type consecutive:',a['key'],b['key'])
for r in w: print(r['n'],r['date'],r['time'],r['key'],len(r['youtube_title']),len(r['pin_desc']), r['music'])
