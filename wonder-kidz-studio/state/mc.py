import json, sys
cal = json.load(open('calendar.json')); urls = json.load(open('urls.json')) if len(sys.argv) < 3 else {}
def info(r, net, u):
    pub = {"dateTime": f"{r['date']}T{r['time']}:00", "timezone": "America/New_York"}
    base = dict(autoPublish=True, draft=False, descendants=[], hasNotReadNotes=False, shortener=False,
                smartLinkData={"ids": []}, mediaAltText=[], publicationDate=pub, firstCommentText="")
    if net == "tiktok":
        base.update(text=r['tiktok'], media=[u['video']], providers=[{"network": "tiktok"}],
                    tiktokData={"privacyOption": "PUBLIC_TO_EVERYONE", "isAigc": True, "disableComment": False, "disableDuet": False, "disableStitch": False, "autoAddMusic": False, "title": r["hook"]})
    if net == "instagram":
        base.update(text=r['instagram'], media=[u['video']], providers=[{"network": "instagram"}],
                    instagramData={"type": "REEL", "showReelOnFeed": True, "isAiGenerated": True})
    if net == "youtube":
        base.update(text=r['youtube_desc'], media=[u['video']], providers=[{"network": "youtube"}], firstCommentText=r['youtube_pinned_comment'],
                    youtubeData={"title": r['youtube_title'], "type": "short", "privacy": "public", "madeForKids": False, "isAiGeneratedContent": True, "category": "EDUCATION"})
    if net == "pinterest":
        base.update(text=r['pin_desc'], media=[u['pin']], providers=[{"network": "pinterest"}],
                    pinterestData={"boardId": "1140888586794329019", "pinTitle": r['pin_title'], "pinLink": r['pin_link'], "pinNewFormat": True, "isAiGenerated": True})
    return json.dumps(base, ensure_ascii=False)
if __name__ == "__main__":
    n = int(sys.argv[1]); r = cal[n - 1]; k = r['out'].split('/')[-1]; u = urls[k]
    for net in ("tiktok", "instagram", "youtube", "pinterest"):
        print(f"### {net} {r['date']}T{r['time']}:00-05:00"); print(info(r, net, u))
