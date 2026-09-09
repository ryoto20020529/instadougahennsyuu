# -*- coding: utf-8 -*-
"""マスコット：ロングコートチワワ（ブラックタン）"""
import math
from PIL import Image, ImageDraw, ImageFilter

FUR_D   = (60, 47, 50)      # 黒毛
FUR_D2  = (92, 74, 76)      # 黒毛ハイライト
CREAM   = (252, 243, 224)   # 胸・マズルのクリーム
CREAM2  = (236, 220, 191)   # クリーム影
TAN     = (233, 196, 150)   # 眉のタン
EAR_IN  = (238, 199, 192)   # 耳の内側
NOSE    = (46, 36, 38)
INK     = (78, 58, 60)      # 線
EYE     = (66, 42, 38)
BOW_A   = (240, 138, 46)    # リボン橙
BOW_B   = (54, 44, 46)      # リボン黒

def _pt(cx, cy, r, a): return (cx + r * math.cos(a), cy + r * math.sin(a))

def fur_poly(cx, cy, rx, ry, n=26, amp=0.055, twist=0.10, a0=0.0):
    """毛先がとがったふわふわ輪郭"""
    p = []
    for i in range(n):
        b = a0 + 2 * math.pi * i / n
        t = a0 + 2 * math.pi * (i + 0.5) / n + twist
        p.append((cx + rx * math.cos(b), cy + ry * math.sin(b)))
        p.append((cx + rx * (1 + amp) * math.cos(t), cy + ry * (1 + amp) * math.sin(t)))
    return p

def draw_dog(im, cx, cy, s=1.0, mood="normal", blink=False, tilt=0.0, bow=True):
    """cx,cy = 頭の中心。s=1.0 で頭幅およそ360px"""
    d = ImageDraw.Draw(im, "RGBA")
    r = lambda v: v * s
    lw = max(2, int(r(6)))
    X = lambda v: cx + r(v)
    Y = lambda v: cy + r(v)

    # ---- 影 ----
    d.ellipse([X(-250), Y(452), X(280), Y(540)], fill=(150, 120, 128, 46))

    # ---- しっぽ（背面・ふさふさ） ----
    for i, (tx, ty, rr) in enumerate([(238, 348, 74), (300, 286, 78), (338, 208, 78),
                                      (336, 128, 72)]):
        d.polygon(fur_poly(X(tx), Y(ty), r(rr), r(rr * .95), 20, .09, .14, i * .7),
                  fill=FUR_D, outline=INK, width=lw)
    for tx, ty, rr in ((316, 70, 66), (274, 26, 54)):
        d.polygon(fur_poly(X(tx), Y(ty), r(rr), r(rr * .95), 18, .10, .16, 1.3),
                  fill=CREAM, outline=INK, width=lw)
    d.polygon(fur_poly(X(300), Y(60), r(50), r(46), 16, .08, .12, .4), fill=(255, 251, 240))

    # ---- 体（黒） ----
    d.polygon(fur_poly(X(10), Y(312), r(238), r(202), 44, .05, .09), fill=FUR_D, outline=INK, width=lw)
    # 後ろ足
    d.polygon(fur_poly(X(185), Y(422), r(92), r(74), 22, .06, .1, .6), fill=FUR_D, outline=INK, width=lw)

    # ---- 胸のクリームの毛 ----
    d.polygon(fur_poly(X(-5), Y(296), r(170), r(184), 40, .05, .09, .4), fill=CREAM, outline=INK, width=lw)
    d.polygon(fur_poly(X(-5), Y(286), r(122), r(140), 32, .05, .1, 1.2), fill=(255, 251, 240))

    # ---- 前足 ----
    for px, py in ((-92, 432), (62, 448)):
        d.polygon(fur_poly(X(px), Y(py), r(62), r(52), 14, .08, .1), fill=CREAM, outline=INK, width=lw)
        for k in range(3):
            d.arc([X(px - 34 + k * 24), Y(py - 6), X(px - 14 + k * 24), Y(py + 26)], 250, 350, fill=CREAM2, width=max(2, int(r(4))))

    # ---- 耳（大きい・房毛つき） ----
    for sx in (-1, 1):
        bx, by = X(sx * 118), Y(-96)
        tipx, tipy = X(sx * 258 + sx * tilt * 40), Y(-330 + abs(tilt) * 10)
        base2 = (X(sx * 18), Y(-176))
        # 外側の房毛
        for k in range(7):
            f = k / 6
            ex = bx + (tipx - bx) * f + sx * r(30) * math.sin(f * 3)
            ey = by + (tipy - by) * f
            d.polygon(fur_poly(ex, ey, r(48 - 22 * f), r(54 - 24 * f), 14, .12, .2 * sx, k),
                      fill=FUR_D, outline=INK, width=lw)
        d.polygon([(bx, by), (tipx, tipy), base2], fill=FUR_D, outline=INK, width=lw)
        # 内側
        ix, iy = (bx * .55 + tipx * .45), (by * .55 + tipy * .45)
        d.polygon([(bx * .8 + base2[0] * .2, by * .9 + base2[1] * .1),
                   (tipx * .82 + bx * .18, tipy * .82 + by * .18),
                   (base2[0] * .55 + bx * .45, base2[1] * .75 + by * .25)],
                  fill=EAR_IN)
        d.polygon(fur_poly(ix, iy + r(30), r(30), r(48), 14, .12, .2 * sx, 2), fill=(246, 224, 196, 190))

    # ---- 頭 ----
    d.polygon(fur_poly(X(0), Y(-10), r(186), r(168), 30, .085, .14), fill=FUR_D, outline=INK, width=lw)
    d.polygon(fur_poly(X(-74), Y(-76), r(76), r(50), 18, .04, .08), fill=(72, 57, 59))
    # マズル周りのクリーム
    d.polygon(fur_poly(X(0), Y(70), r(152), r(100), 28, .07, .12, .5), fill=CREAM, outline=None)
    d.polygon(fur_poly(X(0), Y(80), r(112), r(76), 24, .05, .1, 1.0), fill=(255, 252, 244))
    # 頬のクリーム
    for sx in (-1, 1):
        d.polygon(fur_poly(X(sx * 150), Y(36), r(52), r(66), 14, .16, .3 * sx), fill=CREAM)

    # ---- タンの眉 ----
    for sx in (-1, 1):
        d.ellipse([X(sx * 84 - 42), Y(-126), X(sx * 84 + 42), Y(-84)], fill=TAN)

    # ---- 目 ----
    ew, eh = r(58), r(64)
    if mood == "surprised":
        ew, eh = r(64), r(74)
    for sx in (-1, 1):
        ex, ey = X(sx * 88), Y(-6)
        if blink or mood == "sleepy":
            d.arc([ex - ew, ey - eh * .6, ex + ew, ey + eh * .6], 200, 340, fill=INK, width=max(4, int(r(10))))
            continue
        d.ellipse([ex - ew, ey - eh, ex + ew, ey + eh], fill=EYE, outline=(40, 28, 28), width=max(2, int(r(4))))
        d.ellipse([ex - ew * .96, ey - eh * .5, ex + ew * .96, ey + eh], fill=(38, 26, 26))
        # ハート型のハイライト
        hx, hy, hr = ex - ew * .3, ey - eh * .42, ew * .38
        d.ellipse([hx - hr, hy - hr * .9, hx + hr * .1, hy + hr * .5], fill=(255, 255, 255))
        d.ellipse([hx - hr * .1, hy - hr * .9, hx + hr, hy + hr * .5], fill=(255, 255, 255))
        d.polygon([(hx - hr, hy + hr * .15), (hx + hr, hy + hr * .15), (hx, hy + hr * 1.15)], fill=(255, 255, 255))
        d.ellipse([ex + ew * .2, ey + eh * .3, ex + ew * .62, ey + eh * .72], fill=(255, 255, 255, 220))
        d.ellipse([ex - ew * .75, ey + eh * .35, ex - ew * .5, ey + eh * .6], fill=(255, 255, 255, 170))
        d.arc([ex - ew * 1.05, ey - eh * 1.18, ex + ew * 1.05, ey + eh * .5], 195, 345,
              fill=(52, 38, 40), width=max(3, int(r(8))))

    # ---- 鼻・口 ----
    nx, ny = X(0), Y(46)
    d.polygon([(nx - r(34), ny - r(14)), (nx + r(34), ny - r(14)), (nx, ny + r(26))], fill=NOSE)
    d.ellipse([nx - r(34), ny - r(30), nx + r(34), ny + r(6)], fill=NOSE)
    if mood == "surprised":
        d.ellipse([nx - r(30), ny + r(34), nx + r(30), ny + r(86)], fill=(150, 84, 88))
    elif mood == "sleepy":
        d.ellipse([nx - r(22), ny + r(34), nx + r(22), ny + r(80)], fill=(150, 84, 88))
    else:
        for sx in (-1, 1):
            d.arc([nx + sx * r(30) - r(30), ny + r(20), nx + sx * r(30) + r(30), ny + r(66)],
                  0 if sx < 0 else 20, 160 if sx < 0 else 180, fill=INK, width=max(3, int(r(8))))
    if mood == "worry":
        for sx in (-1, 1):
            d.line([(X(sx * 116), Y(-96)), (X(sx * 56), Y(-72))], fill=INK, width=max(3, int(r(8))))

    # ---- リボン ----
    if bow:
        bxc, byc = X(0), Y(212)
        for sx in (-1, 1):
            pts = [(bxc + sx * r(16), byc), (bxc + sx * r(96), byc - r(46)),
                   (bxc + sx * r(104), byc + r(6)), (bxc + sx * r(96), byc + r(48))]
            d.polygon(pts, fill=BOW_B, outline=INK, width=max(2, int(r(4))))
            for k in range(3):
                d.line([(bxc + sx * r(34 + k * 24), byc - r(34 - k * 4)),
                        (bxc + sx * r(40 + k * 24), byc + r(36 - k * 4))], fill=BOW_A, width=max(3, int(r(9))))
        d.ellipse([bxc - r(30), byc - r(30), bxc + r(30), byc + r(30)], fill=BOW_A, outline=INK, width=max(2, int(r(4))))
        d.line([(bxc, byc - r(30)), (bxc, byc + r(24))], fill=(190, 96, 30), width=max(2, int(r(5))))
        d.line([(bxc - r(16), byc - r(26)), (bxc - r(12), byc + r(20))], fill=(190, 96, 30), width=max(2, int(r(4))))
        d.line([(bxc + r(16), byc - r(26)), (bxc + r(12), byc + r(20))], fill=(190, 96, 30), width=max(2, int(r(4))))
        d.line([(bxc, byc - r(38)), (bxc + r(6), byc - r(28))], fill=(96, 150, 76), width=max(3, int(r(7))))

if __name__ == "__main__":
    im = Image.new("RGBA", (1080, 1400), (245, 240, 246, 255))
    draw_dog(im, 540, 620, 1.0, "normal", False)
    im.convert("RGB").save("dog_test.png")
    im2 = Image.new("RGBA", (1080, 600), (245, 240, 246, 255))
    for i, m in enumerate(["surprised", "sleepy", "worry"]):
        draw_dog(im2, 180 + i * 360, 260, 0.42, m, False)
    im2.convert("RGB").save("dog_moods.png")
    print("ok")
