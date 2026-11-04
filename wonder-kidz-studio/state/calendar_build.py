import json, sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import ITEMS, SHORT
WK='/home/claude/wk'
start=datetime.date(2026,11,4); times=["09:00","13:00","20:00"]
cal=[]; tr={}
for n,it in enumerate(ITEMS):
    item=json.load(open(f"{WK}/item_{it['key']}.json"))
    day=start+datetime.timedelta(days=n//3); t=times[n%3]
    tags=it['tags']
    tt=f"{it['tt']}\n{'Free printables' if it['book']=='activity' else 'Coloring book + free printables'} in bio. " + " ".join(tags[:4]+["#christmaswithkids"])
    ig=it['ig']+"\n\n"+" ".join(tags+["#christmasactivitiesforkids","#screenfreekids","#kidsactivities"] if "#kidsactivities" not in tags else tags+["#christmasactivitiesforkids","#screenfreekids","#preschoolactivities"])
    ytd=f"{it['ytd']}\n🎁 Free Christmas printables + our coloring book: {SHORT}\n#christmasactivities #kidsactivities #shorts"
    row=dict(n=n+1,key=it['key'],book=it['book'],date=str(day),time=t,timezone="America/New_York",hook_type=it['hook_type'],hook=it['hook'],
             music=item['music'].split('/')[-1],out=f"posts/{n+1:02d}_{it['key']}",tiktok=tt,instagram=ig,youtube_title=it['yt'],
             youtube_desc=ytd,youtube_pinned_comment=f"🎁 Free Christmas printables: {SHORT}",pin_title=it['pt'],pin_desc=it['pd'],
             pin_link=it['pin_link'],instagram_format="reel",status="draft")
    assert len(it['yt'])<=60,(it['yt'],len(it['yt'])); assert len(it['pt'])<100,it['pt']; assert len(it['pd'])<500,len(it['pd'])
    assert len(tt)<=2200 and len(ig)<=2200
    tr[row['music']]=tr.get(row['music'],0)+1
    cal.append(row)
for a,b in zip(cal,cal[1:]):
    assert a['hook_type']!=b['hook_type'],(a['key'],b['key'])
json.dump(cal,open('calendar.json','w'),indent=1,ensure_ascii=False)
print('posts',len(cal),'max track uses',max(tr.values()))
