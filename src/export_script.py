# -*- coding: utf-8 -*-
"""読み上げ用の原稿をタイムコード付きテキストで書き出す（CapCut等への貼り付け用）"""
import os
from series import EPISODES
from narration import NARRATION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "docs", "読み上げ原稿")
os.makedirs(DST, exist_ok=True)

HEAD = """※ 使い方（CapCutの場合）
   1. テキストを追加して下の「読み上げ」の行を貼り付ける
   2. そのテキストを選んで「テキスト読み上げ」→ 好きな声を選んで生成
   3. 音声が別トラックになるので、貼り付けたテキストは削除してOK
   4. 音声クリップを「開始」の秒数に合わせて配置する
   ＊映像にはすでにテロップが入っています。テキストは音声を作るためだけに使ってください。
"""

def mmss(s):
    return f"{int(s)//60}:{int(s)%60:02d}"

def ep_text(n):
    ep = EPISODES[n]
    L = [ep["title"], f"尺 {ep['scenes'][-1]['t1']}秒 / {len(ep['scenes'])}シーン",
         "=" * 46, "", HEAD, "=" * 46, ""]
    for i, (s, txt) in enumerate(zip(ep["scenes"], NARRATION[n]), 1):
        L += [f"■ シーン{i}　開始 {mmss(s['t0'])}　（{mmss(s['t0'])} - {mmss(s['t1'])} / {s['t1']-s['t0']}秒）",
              f"　テロップ　： {' '.join(s['telop'])}",
              f"　読み上げ　： {txt}", ""]
    L += ["-" * 46, "▼ 貼り付け用（読み上げ原稿だけ）", ""]
    for i, txt in enumerate(NARRATION[n], 1):
        L.append(f"{i}) {txt}")
    L.append("")
    return "\n".join(L)

def main():
    allt = []
    for n in sorted(EPISODES):
        t = ep_text(n)
        name = f"{n:02d}_{EPISODES[n]['file']}.txt"
        with open(os.path.join(DST, name), "w", encoding="utf-8") as f:
            f.write(t)
        allt.append(t)
        print("書き出し:", name)
    with open(os.path.join(ROOT, "docs", "読み上げ原稿_全10話.txt"), "w", encoding="utf-8") as f:
        f.write(("\n\n" + "#" * 60 + "\n\n").join(allt))
    print("書き出し: docs/読み上げ原稿_全10話.txt")

if __name__ == "__main__":
    main()
