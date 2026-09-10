# -*- coding: utf-8 -*-
"""外部アプリ（CapCut等）で好きな音声を乗せるための素材を書き出す。
  out_novoice/  ナレーションなし・BGMのみ（そのまま読み込んで音声を足すだけ）
  out_silent/   完全無音（BGMも自分で選びたい場合）
  assets/bgm/   BGM単体のmp3
"""
import os, sys, subprocess
import imageio_ffmpeg
from series import EPISODES
import bgm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_OUT = os.path.join(ROOT, "out")
NOVOICE = os.path.join(ROOT, "out_novoice")
SILENT = os.path.join(ROOT, "out_silent")
BGMDIR = os.path.join(ROOT, "assets", "bgm")
TMP = os.path.join(HERE, "tmp_audio")
for d in (NOVOICE, SILENT, BGMDIR, TMP):
    os.makedirs(d, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
BGM_LEVEL = 0.34

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def make(n):
    ep = EPISODES[n]
    total = ep["scenes"][-1]["t1"]
    vid = os.path.join(SRC_OUT, ep["file"] + ".mp4")
    wav = os.path.join(TMP, f"ep{n:02d}_bgm.wav")
    bgm.save(wav, total, seed=n)

    # BGM単体（mp3）
    mp3 = os.path.join(BGMDIR, ep["file"] + "_bgm.mp3")
    run([FF, "-y", "-loglevel", "error", "-i", wav, "-af", f"volume={BGM_LEVEL}",
         "-b:a", "192k", mp3])

    # ナレーションなし・BGMのみ
    out1 = os.path.join(NOVOICE, ep["file"] + "_bgmonly.mp4")
    run([FF, "-y", "-loglevel", "error", "-i", vid, "-i", wav,
         "-filter_complex", f"[1:a]volume={BGM_LEVEL},alimiter=limit=0.97[a]",
         "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", "-shortest", out1])

    # 完全無音
    out2 = os.path.join(SILENT, ep["file"] + "_silent.mp4")
    run([FF, "-y", "-loglevel", "error", "-i", vid, "-an", "-c:v", "copy",
         "-movflags", "+faststart", out2])

    print(f"ep{n}: BGMのみ {os.path.getsize(out1)//1024}KB / 無音 {os.path.getsize(out2)//1024}KB / "
          f"BGM単体 {os.path.getsize(mp3)//1024}KB", flush=True)

if __name__ == "__main__":
    for n in ([int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else range(1, 11)):
        make(n)
