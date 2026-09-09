# -*- coding: utf-8 -*-
"""ナレーション音声を合成し、各話の動画に合流させる（Open JTalk + ffmpeg）"""
import os, sys, wave, subprocess, tempfile
import imageio_ffmpeg
from series import EPISODES
from narration import NARRATION

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TMP = os.path.join(HERE, "tmp_audio")
os.makedirs(TMP, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
DIC = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
VOICE = "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice"
LEAD = 0.35        # シーン頭からの間
OVERLAP = 1.0      # 次シーンへの許容はみ出し
MAX_TEMPO = 1.35

def run(cmd, inp=None):
    subprocess.run(cmd, input=inp, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wav_dur(p):
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()

def synth(text, path, rate=1.0):
    run(["open_jtalk", "-x", DIC, "-m", VOICE, "-r", str(rate), "-fm", "-0.4",
         "-ow", path], inp=text.encode("utf-8"))

def build_audio(n):
    ep = EPISODES[n]
    scenes, texts = ep["scenes"], NARRATION[n]
    total = scenes[-1]["t1"]
    parts = []
    for i, (s, txt) in enumerate(zip(scenes, texts)):
        raw = os.path.join(TMP, f"{n:02d}_{i}_raw.wav")
        fin = os.path.join(TMP, f"{n:02d}_{i}.wav")
        synth(txt, raw)
        d = wav_dur(raw)
        last = i == len(scenes) - 1
        window = (s["t1"] - s["t0"]) - LEAD + (0 if last else OVERLAP) - (0.4 if last else 0)
        tempo = 1.0
        if d > window:
            tempo = min(MAX_TEMPO, d / window)
        af = f"atempo={tempo:.3f}," if tempo > 1.001 else ""
        run([FF, "-y", "-loglevel", "error", "-i", raw, "-af",
             af + "aresample=48000,volume=2.2,alimiter=limit=0.95", fin])
        parts.append((s["t0"] + LEAD, fin, wav_dur(fin), tempo))
        if wav_dur(fin) > window + 0.35:
            print(f"  ! ep{n} scene{i}: {wav_dur(fin):.1f}s > 窓{window:.1f}s (tempo {tempo:.2f})")
    # ミックス
    cmd = [FF, "-y", "-loglevel", "error"]
    for _, p, _, _ in parts:
        cmd += ["-i", p]
    fl = "".join(f"[{i}]adelay={int(st*1000)}|{int(st*1000)}[a{i}];" for i, (st, _, _, _) in enumerate(parts))
    fl += "".join(f"[a{i}]" for i in range(len(parts)))
    fl += f"amix=inputs={len(parts)}:normalize=0:dropout_transition=0,"
    fl += f"apad,atrim=0:{total},afade=t=out:st={total-0.6}:d=0.6,alimiter=limit=0.97[out]"
    track = os.path.join(TMP, f"ep{n:02d}_voice.wav")
    run(cmd + ["-filter_complex", fl, "-map", "[out]", "-ar", "48000", "-ac", "2", track])
    return track

def mux(n):
    ep = EPISODES[n]
    vid = os.path.join(OUT, ep["file"] + ".mp4")
    track = build_audio(n)
    tmp = os.path.join(TMP, ep["file"] + "_av.mp4")
    run([FF, "-y", "-loglevel", "error", "-i", vid, "-i", track,
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", "-shortest", tmp])
    os.replace(tmp, vid)
    print(f"DONE ep{n}: 音声を合流 -> {vid} ({os.path.getsize(vid)//1024}KB)", flush=True)

if __name__ == "__main__":
    for n in ([int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else range(1, 11)):
        mux(n)
