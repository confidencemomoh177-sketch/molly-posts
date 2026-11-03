"""Book Social Media Autopilot - royalty-free background music made in code.

Usage:  python3 make_music.py <mood> [out_dir]
  moods: christmas, cookbook, crafts, children, exam, selfhelp, travel, faith, markets
Melodies used are public domain (published before 1929) or written fresh here; every recording is original.
"""
import sys, os, wave, glob
import numpy as np, fluidsynth

SR = 44100
SF = next(iter(glob.glob("/usr/share/sounds/sf2/TimGM6mb.sf2") + glob.glob("/usr/share/sounds/sf2/*.sf2") + glob.glob("/usr/share/soundfonts/*.sf2")), None)

CH = {"C": [60, 64, 67], "F": [53, 57, 60], "G": [55, 59, 62], "G7": [55, 59, 65], "D7": [50, 54, 60],
      "Am": [57, 60, 64], "E7": [52, 56, 62], "Dm": [50, 53, 57], "Em": [52, 55, 59], "Fmaj7": [53, 57, 64],
      "Cmaj7": [60, 64, 71]}
ROOT = {"C": 48, "F": 41, "G": 43, "G7": 43, "D7": 38, "Am": 45, "E7": 40, "Dm": 38, "Em": 40,
        "Fmaj7": 41, "Cmaj7": 48}

SONGS = {
    "jingle_bells": dict(bpb=4, pickup=0, melody=[
        (64,1),(64,1),(64,2),(64,1),(64,1),(64,2),(64,1),(67,1),(60,1.5),(62,.5),(64,4),
        (65,1),(65,1),(65,1.5),(65,.5),(65,1),(64,1),(64,1),(64,.5),(64,.5),(64,1),(62,1),(62,1),(64,1),(62,2),(67,2),
        (64,1),(64,1),(64,2),(64,1),(64,1),(64,2),(64,1),(67,1),(60,1.5),(62,.5),(64,4),
        (65,1),(65,1),(65,1),(65,1),(65,1),(64,1),(64,1),(64,.5),(64,.5),(67,1),(67,1),(65,1),(62,1),(60,4)],
        chords="C C C C F C D7 G7 C C C C F C G7 C".split()),
    "we_wish": dict(bpb=3, pickup=1, melody=[
        (67,1),(72,1),(72,.5),(74,.5),(72,.5),(71,.5),(69,1),(69,1),(69,1),
        (74,1),(74,.5),(76,.5),(74,.5),(72,.5),(71,1),(67,1),(67,1),
        (76,1),(76,.5),(77,.5),(76,.5),(74,.5),(72,1),(69,1),(67,.5),(67,.5),
        (69,1),(74,1),(71,1),(72,3)], chords="C F D7 G E7 F G7 C".split()),
    "deck_the_halls": dict(bpb=4, pickup=0, melody=[
        (67,1.5),(65,.5),(64,1),(62,1),(60,1),(62,1),(64,1),(60,1),
        (62,.5),(64,.5),(65,.5),(62,.5),(64,1.5),(62,.5),(60,1),(59,1),(60,2)] * 2,
        chords="C C G7 C C C G7 C".split()),
}
LOOPS = {
    "warm":    "C Am F G C Am F G".split(),
    "gentle":  "Cmaj7 Fmaj7 Cmaj7 Fmaj7 Am F C G".split(),
    "bright":  "C G Am F C G F G".split(),
}
MELODY_SHAPES = [[2, 1, 0, 1], [0, 1, 2, 2], [2, 2, 1, 0], [1, 2, 1, 0]]
STYLES = {
    "musicbox": (10, 8, 32, 1.0, "arp", True), "piano": (0, 0, 32, 0.9, "block", True),
    "bells": (9, 45, 33, 1.08, "pluck", True), "strings": (73, 48, 32, 0.85, "pad", True),
    "guitar": (24, 24, 32, 1.0, "arp", True), "accordion": (21, 45, 33, 1.0, "pluck", True),
}
MOODS = {  # European Christmas markets: accordion/bells travel loops + public-domain carols
    "markets": [("bright", "accordion", 108), ("warm", "accordion", 100), ("warm", "bells", 104),
                ("bright", "bells", 110), ("gentle", "guitar", 96),
                ("we_wish", "accordion", 112), ("deck_the_halls", "bells", 116),
                ("jingle_bells", "musicbox", 132), ("we_wish", "musicbox", 112),
                ("gentle", "accordion", 98), ("warm", "guitar", 100), ("deck_the_halls", "piano", 116), ("jingle_bells", "bells", 132)],
}

def loop_song(prog):
    mel = []
    for i, c in enumerate(prog):
        for j in MELODY_SHAPES[i % 4]:
            mel.append((CH[c][j] + 12, 1))
    return dict(bpb=4, pickup=0, melody=mel, chords=prog)

def events(song, style, bpm):
    s = SONGS[song] if song in SONGS else loop_song(LOOPS[song])
    mprog, aprog, bprog, tf, acc, mel_on = STYLES[style]
    spb = 60.0 / (bpm * tf)
    high = style in ("musicbox", "bells")
    ev, t = [], 0.0
    for rep in range(2):
        start = t
        for n, dur in s["melody"]:
            if mel_on:
                ev.append((t, dur * spb * 0.95, 0, n + 12 if high else n, 100))
            t += dur * spb
        bt = start + s["pickup"] * spb
        bpb = s["bpb"]
        for c in s["chords"]:
            tones, root = CH[c], ROOT[c]
            ev.append((bt, bpb * spb * 0.9, 2, root, 85))
            if acc == "arp":
                seq = tones + [tones[1]] if bpb == 4 else tones
                for i in range(bpb * 2):
                    ev.append((bt + i * spb / 2, spb * 0.9, 1, seq[i % len(seq)] + 12, 55))
            elif acc == "block":
                for b in range(bpb):
                    for tn in tones:
                        ev.append((bt + b * spb, spb * 0.8, 1, tn, 50 if b else 62))
            elif acc == "pluck":
                for b in range(bpb):
                    for tn in tones:
                        ev.append((bt + b * spb, spb * 0.4, 1, tn + 12, 60))
            else:
                for tn in tones:
                    ev.append((bt, bpb * spb, 1, tn, 60))
            bt += bpb * spb
    return ev, (mprog, aprog, bprog)

def save(a, out):
    a = a / max(1e-9, np.abs(a).max()) * 0.85
    fade = int(2.5 * SR)
    a[-fade:] *= np.linspace(1, 0, fade)[:, None]
    a[:int(.05 * SR)] *= np.linspace(0, 1, int(.05 * SR))[:, None]
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())
    return len(a) / SR

def render(song, style, bpm, out):
    ev, progs = events(song, style, bpm)
    fs = fluidsynth.Synth(samplerate=SR, gain=0.5)
    sfid = fs.sfload(SF)
    for ch, p in enumerate(progs):
        fs.program_select(ch, sfid, 0, p)
    fs.set_reverb(0.7, 0.4, 0.9, 0.5)
    msgs = sorted([m for st, du, ch, n, v in ev for m in ((st, 1, ch, n, v), (st + du, 0, ch, n, 0))],
                  key=lambda m: (m[0], m[1]))
    buf, cur = [], 0
    for tm, on, ch, n, v in msgs:
        tgt = int(tm * SR)
        if tgt > cur:
            buf.append(fs.get_samples(tgt - cur)); cur = tgt
        fs.noteon(ch, n, v) if on else fs.noteoff(ch, n)
    buf.append(fs.get_samples(int(2.5 * SR)))
    fs.delete()
    return save(np.concatenate(buf).astype(np.float32).reshape(-1, 2), out)

if __name__ == "__main__":
    mood = sys.argv[1] if len(sys.argv) > 1 else "markets"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "music"
    os.makedirs(out_dir, exist_ok=True)
    for song, style, bpm in MOODS[mood]:
        f = f"{out_dir}/{mood}_{song}_{style}.wav"
        print(f, round(render(song, style, bpm, f), 1), "s")
