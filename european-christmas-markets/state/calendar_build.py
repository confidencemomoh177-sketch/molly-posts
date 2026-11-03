import json, sys, datetime
sys.path.insert(0,'.')
from items import ITEMS, ORDER
from captions import C
FULL, SHORT = sys.argv[1], sys.argv[2]
start=datetime.date(2026,11,3); times=["09:00","13:00","19:00"]
cal=[]; tracks={}
for n,key in enumerate(ORDER):
    it=next(i for i in ITEMS if i['key']==key); c=C[key]
    item=json.load(open(f'items_{key}.json'))
    day=start+datetime.timedelta(days=n//3); t=times[n%3]
    tt=f"{it['hook']} ✨ {c['tt']} {c['q']}\nFull guide in bio. " + " ".join(c['tags']+["#christmasmarkets","#europetravel"])
    ig=f"{it['hook']}.\n\n{c['ig']}\n\nSave this for your trip planning 🎄\nDates, hours & itineraries for every market are in the guide (link in bio).\n\n" + " ".join(c['tags']+["#christmasmarkets","#europeanchristmasmarkets","#christmasineurope","#europetravel","#wintertravel"])
    ytt=(c['yt']+" #shorts")
    ytd=f"{c['ytd']}\nGet the European Christmas Markets Guide 2026–2027: {SHORT}\n#christmasmarkets #europetravel #shorts"
    row=dict(n=n+1,key=key,date=str(day),time=t,timezone="America/New_York",hook_type=it['hook_type'],hook=it['hook'],
             music=item['music'].split('/')[-1],out=item['out'],tiktok=tt,instagram=ig,youtube_title=ytt,youtube_desc=ytd,
             youtube_pinned_comment=f"📖 The full guide: {SHORT}",pin_title=c['pt'],pin_desc=c['pd'],pin_link=FULL,
             instagram_format="reel",status="draft")
    cal.append(row)
    assert len(ytt)<=60, ytt; assert len(c['pt'])<100; assert len(c['pd'])<500
    tracks[row['music']]=tracks.get(row['music'],0)+1
json.dump(cal,open('calendar.json','w'),indent=1,ensure_ascii=False)
print('max track uses', max(tracks.values()))
for a,b in zip(cal,cal[1:]):
    if a['hook_type']==b['hook_type']: print('same hook type consecutive:',a['key'],b['key'])
