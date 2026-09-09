# -*- coding: utf-8 -*-
import sys, os, math
from PIL import Image
import imageio_ffmpeg
from engine import *
import engine as E
from series import EPISODES, MOTIF

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUTDIR, exist_ok=True)

def render_frame(ep, t):
    dur = ep["scenes"][-1]["t1"]
    s = ep["scenes"][-1]
    for x in ep["scenes"]:
        if x["t0"] <= t < x["t1"]:
            s = x; break
    lt = t - s["t0"]
    im = background(t)
    MOTIF[s["kind"]](im, t, lt, s["t1"] - s["t0"], **s["kw"])
    draw_telop(im, s["telop"], s["subs"], (t - s["t0"]) / 0.45)
    draw_tag(im, ep["title"], t)
    f = min(cl(t / 0.5), cl((dur - t) / 0.7))
    out = im.convert("RGB")
    if f < 1:
        out = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), out, f)
    return out

def build(n, preview=None):
    ep = EPISODES[n]
    dur = ep["scenes"][-1]["t1"]
    if preview is not None:
        render_frame(ep, preview).save(os.path.join(OUTDIR, f"prev_{n:02d}_{int(preview)}.png"))
        return
    path = os.path.join(OUTDIR, ep["file"] + ".mp4")
    total = int(dur * FPS)
    w = imageio_ffmpeg.write_frames(path, (W, H), fps=FPS, quality=8, macro_block_size=1,
                                    output_params=["-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart"])
    w.send(None)
    for i in range(total):
        w.send(render_frame(ep, i / FPS).tobytes())
        if i % 300 == 0: print(f"ep{n}: {i}/{total}", flush=True)
    w.close()
    print(f"DONE ep{n} -> {path} {os.path.getsize(path)//1024}KB", flush=True)

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "prev":
        for n in [int(x) for x in a[1].split(",")]:
            for tt in [float(x) for x in a[2].split(",")]:
                build(n, preview=tt)
        print("preview ok")
    else:
        for n in [int(x) for x in a[0].split(",")]:
            build(n)
