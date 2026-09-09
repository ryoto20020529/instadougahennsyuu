# -*- coding: utf-8 -*-
"""第1話〜第10話のシーン構成とモチーフ描画"""
import math
from PIL import Image, ImageDraw
from engine import *
import engine as E

# ============ モチーフ ============
def M_hero(im, t, lt, dur, mood="normal", zoom=(0.86, 1.05), tilt=0.0, icons_=None, word=None):
    s = lerp(zoom[0], zoom[1], ease(cl(lt / max(0.8, dur * .8))))
    ang = tilt * math.sin(t * 1.6)
    E.dog(im, W / 2, 800 + math.sin(t * 2) * 10, s, mood, (t % 3.4) < 0.13, ang)
    if icons_:
        for i, k in enumerate(icons_):
            a = int(255 * ease(cl((lt - .6 - i * .5) / .6)))
            icon(im, k, 210 + i * 660, 470 + math.sin(t * 2 + i) * 14, .8, a)
    if word:
        label(im, W / 2, 1180, word, int(255 * ease(cl((lt - .5) / .7))))

def M_trio(im, t, lt, dur, arrows=True):
    E.dog(im, W / 2, 640 + math.sin(t * 2) * 8, 0.55, "normal", (t % 3.4) < 0.13)
    for i, (col, face) in enumerate([(WHITE_B, "shy"), (BLACK_B, "worry"), (RED_B, "pain")]):
        ap = ease(cl((lt - .5 - i * .75) / .7))
        if ap <= 0: continue
        cx = 250 + i * 290
        cy = 1120 + math.sin(t * 2.2 + i) * 8 + (1 - ap) * 60
        guest(im, "bump", cx, cy, 108 * ap, face, col, t,
              glow=(255, 120, 110, 90) if i == 2 else None)
        label(im, cx, 1236, ["白ニキビ", "黒ニキビ", "赤ニキビ"][i], int(255 * ease(cl((lt - 1.1 - i * .75) / .6))))
    if arrows:
        d = ImageDraw.Draw(im, "RGBA")
        for i in range(2):
            a = int(210 * ease(cl((lt - 1.9 - i * .75) / .5)))
            if a > 0:
                x = 395 + i * 290
                d.polygon([(x - 22, 1100), (x + 22, 1120), (x - 22, 1140)], fill=(255, 255, 255, a))

def M_focus(im, t, lt, dur, c0=WHITE_B, c1=None, f0="shy", f1=None, word=None,
            glow=None, ramp=(1.2, 5.5), swell=False, rings=False, scar=0, pores=None):
    k = ease(cl((lt - ramp[0]) / max(.1, ramp[1] - ramp[0]))) if c1 else 0.0
    col = clerp(c0, c1, k) if c1 else c0
    face = (f1 if k > .5 else f0) if f1 else f0
    sw = k * (.6 + .4 * (.5 + .5 * math.sin(t * 5))) if swell else 0.0
    E.dog(im, 236, 1120 + math.sin(t * 2) * 8, 0.40, "normal", (t % 3.4) < 0.13)
    cx, cy = 660, 860 + math.sin(t * 2) * 8
    if rings: fx_rings(im, cx, cy, 250, t)
    g = glow
    if callable(glow): g = glow(k, t)
    guest(im, "bump", cx, cy, 250, face, col, t, swell=sw, glow=g)
    if scar > 0: fx_scar(im, cx, cy + 300, scar * ease(cl((lt - 1.0) / 3.0)))
    if scar < 0: fx_scar(im, cx, cy + 300, -scar * (1 - ease(cl((lt - 0.8) / 4.5))))
    if pores: fx_pores(im, cx, cy, 240, *pores)
    if word: label(im, cx, 1176, word, int(255 * ease(cl(lt / .8))))

def M_guest(im, t, lt, dur, kind="bump", color=None, face="shy", word=None, fx=None,
            dogmood="normal", extra=None):
    E.dog(im, 320, 880 + math.sin(t * 2) * 10, 0.56, dogmood, (t % 3.4) < 0.13)
    ap = ease(cl(lt / .8))
    gx, gy, gr = 782, 1010 + math.sin(t * 2.2 + 1) * 9, 180 * ap
    glow = (255, 244, 200, 110) if fx == "sparkle" else None
    if fx == "steam": fx_steam(im, gx, gy, t)
    guest(im, kind, gx, gy, gr, face, color, t, glow=glow)
    if fx == "sparkle": fx_sparkles(im, gx, gy, 200, t)
    if fx == "foam": fx_foam(im, gx, gy, t)
    if fx == "zzz": fx_zzz(im, gx, gy - 120, t)
    if extra: icon(im, extra, 250, 470, .78, int(255 * ease(cl((lt - .6) / .6))))
    if word: label(im, gx, 1214, word, int(255 * ease(cl((lt - .5) / .7))))

def M_pinch(im, t, lt, dur, word=None):
    E.dog(im, 250, 1130 + math.sin(t * 2) * 8, 0.38, "worry", (t % 3.4) < 0.13)
    cx, cy = 660, 900
    dip = ease(cl((lt - 1.0) / 2.2)) * (0.5 + 0.5 * math.sin(t * 2.2))
    guest(im, "bump", cx, cy + 12 * dip, 230, "pain", RED_B, t, glow=(255, 110, 100, 110))
    finger(im, cx, cy - 340 + 190 * dip, 1.0, 8 * math.sin(t * 1.4))
    if word: label(im, cx, 1200, word, int(255 * ease(cl(lt / .8))))

def M_care(im, t, lt, dur, color=RED_B, face="shy", word=None):
    E.dog(im, 330, 900 + math.sin(t * 2) * 10, 0.56, "smile", (t % 3.4) < 0.13)
    gx, gy = 790, 1020
    guest(im, "bump", gx, gy, 175, face, color, t, glow=(255, 236, 214, 120))
    cream_dab(im, gx - 40 + 20 * math.sin(t * 2), gy - 210 + 16 * math.sin(t * 2.6), 1.0)
    fx_sparkles(im, gx, gy, 190, t, 6, (255, 252, 236, 210))
    if word: label(im, gx, 1214, word, int(255 * ease(cl((lt - .5) / .7))))

def M_mask(im, t, lt, dur, variant="rub", word=None):
    E.dog(im, 300, 900 + math.sin(t * 2) * 10, 0.54, "worry" if variant != "swap" else "smile",
          (t % 3.4) < 0.13)
    mx, my = 716, 900
    if variant == "steam": fx_steam(im, mx, my + 60, t)
    mask_shape(im, mx, my + (14 * math.sin(t * 6) if variant == "rub" else 0), 1.0)
    if variant == "rub":
        guest(im, "bump", mx - 40, my + 240, 130, "pain", RED_B, t, glow=(255, 110, 100, 110))
    if variant == "swap":
        d = ImageDraw.Draw(im, "RGBA")
        a = int(255 * ease(cl((lt - 1.2) / 1.2)))
        mask_shape(im, mx + 40, my + 300 - 60 * ease(cl((lt - 1.2) / 2.0)), .7)
        fx_sparkles(im, mx, my, 250, t, 7, (255, 255, 255, a))
    if word: label(im, mx, 1210, word, int(255 * ease(cl((lt - .5) / .7))))

def M_icons(im, t, lt, dur, kinds=(), word=None, mood="smile"):
    E.dog(im, W / 2, 860 + math.sin(t * 2) * 10, 0.62, mood, (t % 3.4) < 0.13)
    n = len(kinds)
    for i, k in enumerate(kinds):
        a = int(255 * ease(cl((lt - .5 - i * .6) / .6)))
        x = W / 2 + (i - (n - 1) / 2) * 330
        icon(im, k, x, 430 + math.sin(t * 2 + i) * 14, .92, a)
    if word: label(im, W / 2, 1244, word, int(255 * ease(cl((lt - .8) / .7))))

def M_finish(im, t, lt, dur, word=None, guests="trio", faces=None, icons_=None):
    nod = math.sin(t * 2.6) * 14
    E.dog(im, W / 2, 660 + nod, 0.56, "smile", (t % 3.4) < 0.13)
    if guests == "trio":
        for i, col in enumerate([WHITE_B, BLACK_B, RED_B]):
            guest(im, "bump", 250 + i * 290, 1120 + math.sin(t * 2.2 + i) * 8, 104, "happy", col, t)
    elif guests:
        kind, col = guests
        guest(im, kind, W / 2 + 300, 1110 + math.sin(t * 2.2) * 8, 130, faces or "happy", col, t)
        fx_sparkles(im, W / 2 + 300, 1110, 150, t, 6)
    if icons_:
        for i, k in enumerate(icons_):
            icon(im, k, 200 + i * 680, 430, .8, 255)
    if word: label(im, W / 2, 1246, word, int(255 * ease(cl((lt - .4) / .8))))

MOTIF = dict(hero=M_hero, trio=M_trio, focus=M_focus, guest=M_guest, pinch=M_pinch,
             care=M_care, mask=M_mask, icons=M_icons, finish=M_finish)

# ============ 話数データ ============
T6 = [(0, 3), (3, 12), (12, 25), (25, 35), (35, 45), (45, 50)]
T1 = [(0, 3), (3, 12), (12, 20), (20, 30), (30, 40), (40, 50)]

def sc(times, i, telop, subs, motif, **kw):
    return dict(t0=times[i][0], t1=times[i][1], telop=telop, subs=subs, kind=motif, kw=kw)

EPISODES = {
1: dict(title="第1話｜白・黒・赤ニキビの違い", file="ep01_nikibi_shurui", scenes=[
  sc(T1,0,["そのニキビ、","もう進行してるかも"],["そのニキビ、もう進行してるかもしれないんですよね"],"hero",mood="surprised",zoom=(.84,1.04)),
  sc(T1,1,["白→黒→赤ニキビ","これ全部“進行度”の話"],["白から黒、黒から赤へ変わっていく","これは全部“進行度”の違い"],"trio"),
  sc(T1,2,["白ニキビ＝毛穴が","詰まり始めた初期段階"],["炎症はまだ起きていない","一番ケアしやすい状態"],"focus",c0=WHITE_B,word="初期段階",glow=(255,240,200,90)),
  sc(T1,3,["酸化すると","黒ニキビになる"],["色が変わっただけに見えるけれど","“時間が経った”というサイン"],"focus",c0=WHITE_B,c1=BLACK_B,f0="shy",f1="worry",word="酸化",ramp=(1.2,5.5)),
  sc(T1,4,["さらに炎症が進むと","赤ニキビに"],["ここまで来ると","跡が残るリスクも上がる"],"focus",c0=BLACK_B,c1=RED_B,f0="worry",f1="pain",word="炎症",ramp=(1.0,5.5),swell=True,rings=True),
  sc(T1,5,["早い段階でケアするほど","跡になりにくい"],["白ニキビのうちに触らずケア","▶ 保存推奨"],"finish",word="白のうちにケア"),
]),
2: dict(title="第2話｜ニキビを潰してはいけない理由", file="ep02_tsubusanai", scenes=[
  sc(T6,0,["そのニキビ、","潰しそうになったことない？"],["そのニキビ、潰しそうになったことないですか"],"hero",mood="worry",zoom=(.84,1.02)),
  sc(T6,1,["潰す＝","炎症を広げる行為"],["一瞬スッキリした気になるけれど","中の炎症を広げてるだけ"],"pinch",word="つまむのはNG"),
  sc(T6,2,["中の炎症が","周りの組織に広がる"],["触った刺激で炎症が広がると","ダメージが周りまで及ぶ"],"focus",c0=RED_B,f0="pain",word="炎症が拡大",rings=True,glow=(255,90,80,140)),
  sc(T6,3,["色素沈着・クレーター跡の","リスクが上がる"],["跡が残りやすくなる"],"focus",c0=(206,118,110),f0="worry",word="跡のリスク",scar=1.0),
  sc(T6,4,["触りたくなったら","保湿＋刺激を避ける"],["触りたくなったときほど","保湿して刺激を与えない"],"care",color=(238,150,140),face="shy",word="保湿でケア"),
  sc(T6,5,["潰したくなったら","深呼吸"],["一回深呼吸、くらいで考える","▶ 保存推奨"],"finish",word="まず深呼吸",guests=("bump",(238,150,140)),faces="happy"),
]),
3: dict(title="第3話｜グルタチオンと抗酸化ケア", file="ep03_glutathione", scenes=[
  sc(T6,0,["肌のくすみ、","実は“酸化”が原因かも"],["肌のくすみ、実は“酸化”が原因かもしれない"],"hero",mood="surprised",zoom=(.84,1.03)),
  sc(T6,1,["グルタチオン＝","体内の抗酸化物質"],["もともと体内にある","抗酸化物質のこと"],"guest",kind="pearl",face="happy",word="グルタチオン",fx="sparkle"),
  sc(T6,2,["メラニンの生成に","関わるとされる成分"],["肌のトーンや透明感のケアとして","注目されている成分"],"guest",kind="pearl",face="happy",word="抗酸化",fx="sparkle"),
  sc(T6,3,["“白玉点滴”の","成分としても有名"],["サプリで摂る人も増えている"],"guest",kind="pearl",face="shy",word="白玉点滴",fx="sparkle",extra="drip"),
  sc(T6,4,["効果には個人差","生活習慣とセットが前提"],["睡眠や生活習慣とセットで","考えるのが前提"],"icons",kinds=("note","moon"),word="過信はしない",mood="normal"),
  sc(T6,5,["気になったら","成分表示をチェック"],["まずは成分表示を見てみる","▶ 保存推奨"],"finish",word="成分表示を見る",guests=("pearl",(250,249,244))),
]),
4: dict(title="第4話｜皮脂は本当に悪者？", file="ep04_hishi", scenes=[
  sc(T6,0,["皮脂＝悪、","はもう古いかも"],["皮脂＝悪、という考え方はもう古いかも"],"hero",mood="normal",zoom=(.84,1.02),tilt=5),
  sc(T6,1,["皮脂は肌の","バリア機能に必要"],["乾燥や外部刺激から肌を守る","バリアの役割がある"],"guest",kind="droplet",face="sad",word="ひ・し・くん",dogmood="smile"),
  sc(T6,2,["洗いすぎると肌が","“足りない”と勘違いする"],["皮脂を取りすぎると","肌が足りていないと勘違いする"],"guest",kind="droplet",face="sad",word="洗いすぎ",fx="foam"),
  sc(T6,3,["結果、余計に","皮脂が出る悪循環に"],["もっと皮脂を出そうとして","余計にベタつく"],"guest",kind="droplet",face="worry",word="過剰分泌",fx="sparkle"),
  sc(T6,4,["大事なのは","適度な洗顔＋保湿"],["ゼロにするのではなく","洗顔と保湿のバランス"],"care",color=(245,219,150),face="happy",word="バランス"),
  sc(T6,5,["洗いすぎ、","実は逆効果"],["洗いすぎてたかも、と思ったら","▶ 保存推奨"],"finish",word="皮脂とは仲良く",guests=("droplet",(245,219,150))),
]),
5: dict(title="第5話｜洗顔のしすぎが招く悪循環", file="ep05_sengan", scenes=[
  sc(T6,0,["1日に何回","顔洗ってますか"],["1日に何回、顔を洗っていますか"],"hero",mood="normal",zoom=(.84,1.03),icons_=("bottle",)),
  sc(T6,1,["洗いすぎ→乾燥→","バリア機能低下"],["洗いすぎるとバリア機能が落ちて","乾燥しやすくなる"],"guest",kind="cell",face="tired",word="乾燥",fx="foam"),
  sc(T6,2,["乾燥を補おうと","皮脂が過剰分泌"],["乾燥を補おうとして","今度は皮脂が過剰に出てくる"],"guest",kind="cell",face="sad",word="ひび割れ"),
  sc(T6,3,["結果、ニキビが","悪化しやすくなる"],["こうして悪循環になる"],"focus",c0=(250,236,230),c1=(236,150,140),f0="sad",f1="pain",word="悪循環",ramp=(.8,4.0),rings=True),
  sc(T6,4,["基本は朝晩2回、","優しく洗うのが目安"],["朝晩の2回、優しく洗うくらいが目安"],"care",color=(250,236,230),face="happy",word="やさしく2回"),
  sc(T6,5,["洗う回数、","見直してみよう"],["回数を一回見直してみる","▶ 保存推奨"],"finish",word="回数を見直す",guests=("cell",(250,236,230))),
]),
6: dict(title="第6話｜睡眠不足とニキビの関係", file="ep06_suimin", scenes=[
  sc(T6,0,["寝てないだけで","ニキビが増える理由"],["寝てないだけでニキビが増えるって知ってましたか"],"hero",mood="sleepy",zoom=(.84,1.02)),
  sc(T6,1,["睡眠中に","成長ホルモンが分泌される"],["肌の生まれ変わりを促す","成長ホルモンが出るタイミング"],"guest",kind="sleep",face="sleep",word="おやすみ中",fx="zzz",dogmood="sleepy"),
  sc(T6,2,["ターンオーバーを","促す役割がある"],["サイクルが回っていると","古い角質がうまく排出される"],"guest",kind="sleep",face="sleep",word="ターンオーバー",fx="sparkle"),
  sc(T6,3,["睡眠不足だと","このサイクルが乱れる"],["寝不足が続くとサイクルが乱れる"],"guest",kind="sleep",face="tired",word="寝不足",dogmood="worry"),
  sc(T6,4,["古い角質が溜まり","毛穴が詰まりやすくなる"],["古い角質が溜まって","毛穴が詰まりやすくなる"],"focus",c0=(246,230,222),f0="worry",word="毛穴が詰まる",pores=(0.0,1.0)),
  sc(T6,5,["睡眠も","ニキビケアの一部"],["スキンケアと同じくらい睡眠も大事","▶ 保存推奨"],"finish",word="しっかり寝よう",guests=("sleep",(252,244,236)),faces="sleep",icons_=("moon",)),
]),
7: dict(title="第7話｜顎ニキビはホルモンのサイン", file="ep07_agonikibi", scenes=[
  sc(T6,0,["顎ニキビ、","実は体からのサインかも"],["顎にできるニキビ、実は体からのサインかも"],"hero",mood="surprised",zoom=(.84,1.03)),
  sc(T6,1,["生理前は","ホルモンバランスが変化する"],["生理前はホルモンバランスが","変化するタイミング"],"guest",kind="bump",color=(240,168,158),face="worry",word="周期のサイン",extra="calendar"),
  sc(T6,2,["皮脂分泌が","増加しやすいタイミング"],["このタイミングで皮脂の分泌が増えやすい"],"guest",kind="bump",color=(238,152,142),face="worry",word="皮脂が増える",fx="sparkle"),
  sc(T6,3,["顎まわりに","繰り返しできやすい"],["顎まわりに繰り返しできやすくなる"],"focus",c0=(236,140,132),f0="pain",word="顎まわり",rings=True),
  sc(T6,4,["食生活・睡眠の見直しが","対策の第一歩"],["食生活と睡眠を見直すのが第一歩"],"icons",kinds=("veg","moon"),word="生活から整える"),
  sc(T6,5,["周期と肌、","記録してみよう"],["自分の周期と肌の変化を記録する","▶ 保存推奨"],"finish",word="記録が武器になる",guests=("bump",(240,168,158)),icons_=("calendar",)),
]),
8: dict(title="第8話｜ビタミンCがニキビ跡に効く理由", file="ep08_vitaminc", scenes=[
  sc(T6,0,["そのニキビ跡、","放置してませんか"],["そのニキビ跡、放置してませんか"],"hero",mood="worry",zoom=(.84,1.03)),
  sc(T6,1,["ビタミンC＝コラーゲン","生成サポート＋抗酸化"],["ニキビ跡でよく名前が挙がるのがビタミンC"],"guest",kind="lemon",face="happy",word="ビタミンC",fx="sparkle"),
  sc(T6,2,["メラニンの生成を","抑える働きがあるとされる"],["コラーゲン生成をサポートし","メラニンの生成を抑えるとされる"],"guest",kind="lemon",face="happy",word="抗酸化",fx="sparkle"),
  sc(T6,3,["色素沈着ケアの","定番成分"],["色素沈着ケアの定番として使われる"],"focus",c0=(250,224,206),f0="happy",word="跡が薄く",scar=-1.0,glow=(255,244,180,110)),
  sc(T6,4,["紫外線対策とセットじゃないと","効果が出にくい"],["日焼け止めとセットで意識する"],"icons",kinds=("umbrella","sunscreen"),word="UV対策とセット"),
  sc(T6,5,["跡ケア、","成分から見直そう"],["成分から見直してみる","▶ 保存推奨"],"finish",word="成分から選ぶ",guests=("lemon",(250,218,92))),
]),
9: dict(title="第9話｜ナイアシンアミドで皮脂コントロール", file="ep09_niacinamide", scenes=[
  sc(T6,0,["皮脂崩れが","止まらない人へ"],["皮脂崩れが止まらない人へ、なんですけど"],"hero",mood="worry",zoom=(.84,1.02)),
  sc(T6,1,["ナイアシンアミド＝皮脂","バランスを整えるとされる成分"],["皮脂のバランスを整えるサポートを","するとされる成分"],"guest",kind="shield",face="happy",word="ナイアシンアミド"),
  sc(T6,2,["バリア機能の","サポートにも人気"],["肌のバリア機能のケアにも人気"],"guest",kind="shield",face="happy",word="バリアを守る",fx="sparkle"),
  sc(T6,3,["毛穴の目立ちにくさにも","寄与するとされる"],["毛穴を意識したケアとしても選ばれる"],"focus",c0=(250,238,232),f0="happy",word="毛穴が引き締まる",pores=(1.0,0.0)),
  sc(T6,4,["化粧水や美容液の","成分表示でチェックできる"],["化粧水や美容液の成分表示を見てみる"],"icons",kinds=("bottle",),word="成分表示をチェック"),
  sc(T6,5,["成分表示、","見る癖をつけよう"],["見る癖をつけてみる","▶ 保存推奨"],"finish",word="まず裏面を見る",guests=("shield",(206,230,246))),
]),
10: dict(title="第10話｜マスク荒れ（マスクネ）対策", file="ep10_maskne", scenes=[
  sc(T6,0,["マスクをすると","増えるニキビの正体"],["マスクをすると増えるニキビ、正体って知ってますか"],"hero",mood="surprised",zoom=(.84,1.03),icons_=("mask",)),
  sc(T6,1,["原因は摩擦・蒸れ・","雑菌の繁殖"],["マスクの内側の摩擦と蒸れ","それによる雑菌の繁殖"],"mask",variant="rub",word="摩擦"),
  sc(T6,2,["長時間つけっぱなしだと","悪化しやすい"],["長時間つけっぱなしだと","どうしても悪化しやすい"],"mask",variant="steam",word="蒸れ"),
  sc(T6,3,["こまめな交換が","まず大事"],["まず大事なのは、こまめに交換すること"],"mask",variant="swap",word="こまめに交換"),
  sc(T6,4,["低刺激な保湿で","バリア機能を保つ"],["低刺激な保湿でバリア機能を保つ"],"care",color=(240,160,150),face="happy",word="低刺激で保湿"),
  sc(T6,5,["マスク生活の人は","保存必須"],["マスク生活が多い人は必見","▶ 保存推奨"],"finish",word="摩擦と蒸れを減らす",guests=("bump",(240,168,158)),icons_=("mask",)),
]),
}
