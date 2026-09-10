# insta動画編集｜スキンケア解説ショート動画 生成一式

ロングコートチワワのマスコット「ハダハカセ」が解説する、縦型ショート動画（1080×1920 / 各50秒）を
Python だけで生成するツール一式です。第1話〜第10話ぶんの構成・白テロップ・ナレーション音声を同梱しています。

## 完成動画

| 話 | タイトル | ファイル |
|---|---|---|
| 1 | 白・黒・赤ニキビの違い | `out/ep01_nikibi_shurui.mp4` |
| 2 | ニキビを潰してはいけない理由 | `out/ep02_tsubusanai.mp4` |
| 3 | グルタチオンと抗酸化ケア | `out/ep03_glutathione.mp4` |
| 4 | 皮脂は本当に悪者？ | `out/ep04_hishi.mp4` |
| 5 | 洗顔のしすぎが招く悪循環 | `out/ep05_sengan.mp4` |
| 6 | 睡眠不足とニキビの関係 | `out/ep06_suimin.mp4` |
| 7 | 顎ニキビはホルモンのサイン | `out/ep07_agonikibi.mp4` |
| 8 | ビタミンCがニキビ跡に効く理由 | `out/ep08_vitaminc.mp4` |
| 9 | ナイアシンアミドで皮脂コントロール | `out/ep09_niacinamide.mp4` |
| 10 | マスク荒れ（マスクネ）対策 | `out/ep10_maskne.mp4` |

仕様：1080×1920 / 30fps / 50秒 / H.264 + AAC（ナレーション＋BGM入り）

### 好きな音声を乗せたい場合の素材

CapCut等の「テキスト読み上げ」で自分の好きな声に差し替えるための素材も入れています。

| フォルダ | 内容 | 用途 |
|---|---|---|
| `out_novoice/` | ナレーションなし・BGMのみ | **これが基本**。読み込んで読み上げ音声を足すだけ |
| `out_silent/` | 完全無音 | BGMも自分で選びたい場合 |
| `assets/bgm/` | BGM単体（mp3） | 無音版に自分でBGMを乗せる場合 |
| `docs/読み上げ原稿/` | 話数ごとの原稿（タイムコード付き・貼り付け用） | 読み上げ音声を作って配置する |

再生成は `cd src && python3 variants.py`（動画素材）、`python3 export_script.py`（原稿）です。

## ファイル構成

```
src/
  mascot.py     マスコット（ロングコートチワワ）の描画。表情 normal/smile/surprised/worry/sleepy＋まばたき
  engine.py     背景・白テロップ・ゲストキャラ・エフェクト（きらめき／泡／湯気／Zzz／炎症の波紋／毛穴／跡）
  series.py     全10話のシーン構成（タイムコード・テロップ・サブテロップ・演出モチーフ）
  narration.py  各話・各シーンのナレーション原稿
  build.py      映像の書き出し
  bgm.py        BGMの合成（オリジナル・権利フリー）
  audio.py      ナレーション合成＋BGM＋動画への合流
  variants.py   ナレーションなし版／無音版／BGM単体の書き出し
  export_script.py  読み上げ原稿をタイムコード付きテキストで書き出し
docs/           元の台本（第1話／第2〜10話）と読み上げ原稿
out/            完成動画（ナレーション＋BGM）
out_novoice/    ナレーションなし・BGMのみ
out_silent/     完全無音
assets/bgm/     BGM単体（mp3）
```

## セットアップ

```bash
pip install -r requirements.txt
# 日本語フォント（IPAゴシック）
sudo apt-get install -y fonts-ipafont-gothic
# 日本語TTS（音声を付ける場合）
sudo apt-get install -y open-jtalk open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001
```

ffmpeg は `imageio-ffmpeg` に同梱のバイナリを使うため、別途インストールは不要です。

## 使い方

```bash
cd src

# 映像を書き出す（引数は話数。カンマ区切りで複数可、省略で全10話）
python3 build.py 3
python3 build.py 1,2,3

# 途中の1フレームだけ確認する（out/prev_<話数>_<秒>.png）
python3 build.py prev 3 5,15,27,37

# ナレーションとBGMを合成して out/ の動画に合流させる
python3 audio.py 3
python3 audio.py          # 全話

# BGMだけを書き出して確認する（第3話ぶんのシード）
python3 bgm.py bgm.wav 3
```

`build.py` は映像のみを書き出します。`audio.py` は `out/` の動画を音声付きで上書きするので、
映像を作り直したら `audio.py` も同じ話数に対して流し直してください。

## 内容の差し替え

- **テロップ・構成**：`src/series.py` の `EPISODES` を編集します。1シーンは
  `sc(タイムコード, シーン番号, [テロップ行], [サブテロップ行], "モチーフ名", **パラメータ)` で定義します。
  モチーフは `hero` `trio` `focus` `guest` `pinch` `care` `mask` `icons` `finish` の9種類です。
- **ナレーション**：`src/narration.py` の該当話・該当シーンの文字列を書き換えます。
  尺に収まらない場合は `audio.py` が最大1.35倍まで自動で早回しし、それでも溢れる場合は警告を出します。
- **話数の追加**：`EPISODES` にキーを追加し、`narration.py` に同じキーで6行の原稿を追加すれば、
  `python3 build.py 11` で書き出せます。

## テロップの仕様

- 白文字＋濃いフチ取り。文字数に応じて 76px / 64px を自動で切り替え
- 下部にグラデーションの影を敷いて可読性を確保
- フェードイン＋わずかに浮き上がるアニメーション
- メインテロップの下に、ナレーションを要約した小さめの白サブテロップを同期表示
- 左上に話数バッジ、画面内に「酸化」「炎症」などのキーワードラベル

## BGMについて

`src/bgm.py` がその場で合成するオリジナル曲です。音源ファイルを使っていないので権利処理は不要で、
クレジット表記もいりません。オルゴール風のメロディ、やわらかいパッド、控えめなキックとハイハットで構成しています。

- 84 BPM、I - V - vi - IV のコード進行、ペンタトニックのメロディをシードから自動生成
- 話数をシードにしているので、10話それぞれキーとメロディが少しずつ違います
- ナレーションが入っている間はBGMが自動で下がります（サイドチェイン・ダッキング）
- 音量は `src/audio.py` の `BGM_LEVEL`（既定 0.34）で調整できます
- 曲調を変えたい場合は `bgm.py` の `PROG`（コード進行）、`PENTA`（音階）、`bpm`、`key` を変更します

市販のBGMや配布音源に差し替える場合は、`audio.py` の `build_bgm()` が返すパスを、その音声ファイルに変えてください。

## ナレーション音声について

Open JTalk（`nitech-jp-atr503-m001`：落ち着いた男性ボイス）で合成しています。
実在人物の声のクローンは行わず、話し方の癖を原稿側で再現する方針です。
別のTTS（ElevenLabs等）で作った音声に差し替える場合は、`out/` の動画に対して次のように合流させてください。

```bash
ffmpeg -i out/ep01_nikibi_shurui.mp4 -i voice.mp3 \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 160k -shortest out.mp4
```
