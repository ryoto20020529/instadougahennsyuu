# -*- coding: utf-8 -*-
"""共通エンジン：背景・白テロップ・マスコット配置・ゲストキャラ・演出エフェクト"""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import mascot

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
F_TELOP = ImageFont.truetype(FONT, 76)
F_TELOP_S = ImageFont.truetype(FONT, 64)
F_SUB = ImageFont.truetype(FONT, 40)
F_TAG = ImageFont.truetype(FONT, 34)
F_LABEL = ImageFont.truetype(FONT, 44)

WHITE_B, BLACK_B, RED_B = (252, 250, 245), (58, 42, 36), (231, 84, 74)
INK = mascot.INK

def lerp(a, b, t): return a + (b - a) * t
def clerp(c1, c2, t): return tuple(int(round(lerp(c1[i], c2[i], t))) for i in range(3))
def ease(t): return t * t * (3 - 2 * t)
def cl(x): return 0.0 if x < 0 else (1.0 if x > 1 else x)

# ---------------- 背景 ----------------
def _bg():
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=clerp((247, 240, 250), (240, 232, 243), y / H))
    rnd = random.Random(7)
    for _ in range(46):
        x, y = rnd.randint(-80, W + 80), rnd.randint(-80, H + 80)
        rr = rnd.randint(60, 210)
        col = rnd.choice([(255, 246, 236), (238, 244, 255), (255, 238, 246), (240, 255, 246), (252, 250, 228)])
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)
    bg = bg.filter(ImageFilter.GaussianBlur(60))
    return bg

BG = _bg()

def sparkle_layer(t, n=16, seed=3):
    """背景のきらきら"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randint(40, W - 40), rnd.randint(180, 1300)
        sz = rnd.randint(14, 40)
        ph = rnd.random() * 6.28
        a = int(200 * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 2.0 + ph))))
        col = rnd.choice([(255, 255, 255, a), (255, 236, 200, a), (226, 236, 255, a)])
        d.polygon([(x, y - sz), (x + sz * .26, y - sz * .26), (x + sz, y),
                   (x + sz * .26, y + sz * .26), (x, y + sz), (x - sz * .26, y + sz * .26),
                   (x - sz, y), (x - sz * .26, y - sz * .26)], fill=col)
    return ov

def background(t):
    im = BG.copy().convert("RGBA")
    im.alpha_composite(sparkle_layer(t))
    return im

# ---------------- マスコット（スプライトキャッシュ） ----------------
_SPR, _SCALED = {}, {}
ANCH = (500, 520)

def _sprite(mood, blink):
    k = (mood, blink)
    if k not in _SPR:
        c = Image.new("RGBA", (1020, 1240), (0, 0, 0, 0))
        mascot.draw_dog(c, ANCH[0], ANCH[1], 1.0, mood, blink)
        _SPR[k] = c
    return _SPR[k]

def dog(im, cx, cy, s=1.0, mood="normal", blink=False, angle=0.0):
    """cx,cy=頭の中心"""
    key = (mood, blink, round(s, 2))
    if key not in _SCALED:
        sp = _sprite(mood, blink)
        _SCALED[key] = sp.resize((max(1, int(sp.width * s)), max(1, int(sp.height * s))), Image.LANCZOS)
        if len(_SCALED) > 260:
            _SCALED.clear(); _SCALED[key] = _SCALED.get(key) or sp.resize(
                (max(1, int(sp.width * s)), max(1, int(sp.height * s))), Image.LANCZOS)
    sp = _SCALED[key]
    ax, ay = ANCH[0] * s, ANCH[1] * s
    if abs(angle) > 0.4:
        sp2 = sp.rotate(angle, resample=Image.BICUBIC, center=(ax, ay))
        sp = sp2
    im.alpha_composite(sp, (int(cx - ax), int(cy - ay)))

# ---------------- ゲストキャラ ----------------
def guest(im, kind, cx, cy, rad, face="shy", color=None, t=0.0, swell=0.0, glow=None):
    d = ImageDraw.Draw(im, "RGBA")
    rr = rad * (1 + 0.10 * swell)
    col = color or {"bump": WHITE_B, "pearl": (250, 249, 244), "droplet": (245, 219, 150),
                    "lemon": (250, 218, 92), "shield": (206, 230, 246), "cell": (250, 236, 230),
                    "sleep": (252, 244, 236)}.get(kind, WHITE_B)
    if glow:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([cx - rr * 1.9, cy - rr * 1.9, cx + rr * 1.9, cy + rr * 1.9], fill=glow)
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(50)))
    d.ellipse([cx - rr * .92, cy + rr * .74, cx + rr * .92, cy + rr * 1.1], fill=(150, 122, 128, 52))
    lw = max(2, int(rad * .05))
    if kind == "droplet":
        d.polygon([(cx, cy - rr * 1.35), (cx + rr * .95, cy + rr * .35), (cx, cy + rr),
                   (cx - rr * .95, cy + rr * .35)], fill=col, outline=INK, width=lw)
        d.ellipse([cx - rr * .96, cy - rr * .45, cx + rr * .96, cy + rr], fill=col, outline=INK, width=lw)
        d.polygon([(cx, cy - rr * 1.4), (cx + rr * .5, cy - rr * .25), (cx - rr * .5, cy - rr * .25)], fill=col)
    elif kind == "lemon":
        d.ellipse([cx - rr, cy - rr * .82, cx + rr, cy + rr * .82], fill=col, outline=INK, width=lw)
        for sx in (-1, 1):
            d.polygon([(cx + sx * rr * .98, cy - rr * .2), (cx + sx * rr * 1.22, cy),
                       (cx + sx * rr * .98, cy + rr * .2)], fill=col, outline=INK, width=lw)
    else:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col, outline=INK, width=lw)
    hl = tuple(min(255, c + 34) for c in col)
    if kind == "droplet":
        d.ellipse([cx - rr * .66, cy - rr * .1, cx - rr * .18, cy + rr * .4], fill=hl)
    elif kind == "lemon":
        d.ellipse([cx - rr * .6, cy - rr * .6, cx - rr * .1, cy - rr * .2], fill=hl)
    else:
        d.ellipse([cx - rr * .7, cy - rr * .76, cx - rr * .04, cy - rr * .14], fill=hl)
    dark = col[0] * .299 + col[1] * .587 + col[2] * .114 < 120
    ink = (245, 240, 238) if dark else INK
    ex, ey, e = rr * .38, -rr * .1, max(3, int(rad * .075))
    if face == "pain":
        for sx in (-1, 1):
            d.line([(cx + sx * ex - rr * .15, cy + ey - rr * .13), (cx + sx * ex + rr * .15, cy + ey + rr * .13)], fill=ink, width=e)
            d.line([(cx + sx * ex - rr * .15, cy + ey + rr * .13), (cx + sx * ex + rr * .15, cy + ey - rr * .13)], fill=ink, width=e)
        d.ellipse([cx - rr * .16, cy + rr * .22, cx + rr * .16, cy + rr * .48], fill=(150, 60, 60))
    elif face == "worry":
        for sx in (-1, 1):
            d.ellipse([cx + sx * ex - rr * .12, cy + ey - rr * .14, cx + sx * ex + rr * .12, cy + ey + rr * .14], fill=ink)
            d.line([(cx + sx * ex - rr * .2, cy + ey - rr * .34), (cx + sx * ex + rr * .16, cy + ey - rr * .22)], fill=ink, width=e)
        d.arc([cx - rr * .22, cy + rr * .28, cx + rr * .22, cy + rr * .5], 190, 350, fill=ink, width=e)
    elif face == "sad":
        for sx in (-1, 1):
            d.ellipse([cx + sx * ex - rr * .13, cy + ey - rr * .15, cx + sx * ex + rr * .13, cy + ey + rr * .15], fill=ink)
            d.ellipse([cx + sx * ex - rr * .07, cy + ey + rr * .16, cx + sx * ex + rr * .07, cy + ey + rr * .42], fill=(140, 196, 236))
        d.arc([cx - rr * .2, cy + rr * .3, cx + rr * .2, cy + rr * .5], 190, 350, fill=ink, width=e)
    elif face == "sleep":
        for sx in (-1, 1):
            d.arc([cx + sx * ex - rr * .17, cy + ey - rr * .12, cx + sx * ex + rr * .17, cy + ey + rr * .16], 200, 340, fill=ink, width=e)
        d.ellipse([cx - rr * .1, cy + rr * .24, cx + rr * .1, cy + rr * .42], fill=(150, 90, 90))
    elif face == "tired":
        for sx in (-1, 1):
            d.arc([cx + sx * ex - rr * .17, cy + ey - rr * .2, cx + sx * ex + rr * .17, cy + ey + rr * .1], 20, 160, fill=ink, width=e)
            for k in range(2):
                d.arc([cx + sx * ex - rr * .2, cy + ey + rr * (.12 + k * .1), cx + sx * ex + rr * .2, cy + ey + rr * (.3 + k * .1)],
                      20, 160, fill=(150, 130, 160), width=max(2, e - 2))
        d.arc([cx - rr * .2, cy + rr * .34, cx + rr * .2, cy + rr * .54], 190, 350, fill=ink, width=e)
    elif face == "happy":
        for sx in (-1, 1):
            d.arc([cx + sx * ex - rr * .17, cy + ey - rr * .1, cx + sx * ex + rr * .17, cy + ey + rr * .2], 200, 340, fill=ink, width=e)
        d.arc([cx - rr * .2, cy + rr * .16, cx + rr * .2, cy + rr * .44], 20, 160, fill=ink, width=e)
        for sx in (-1, 1):
            d.ellipse([cx + sx * rr * .58 - rr * .12, cy + rr * .12, cx + sx * rr * .58 + rr * .12, cy + rr * .3], fill=(250, 190, 190, 190))
    else:  # shy
        for sx in (-1, 1):
            d.arc([cx + sx * ex - rr * .16, cy + ey - rr * .1, cx + sx * ex + rr * .16, cy + ey + rr * .2], 200, 340, fill=ink, width=e)
        d.arc([cx - rr * .17, cy + rr * .2, cx + rr * .17, cy + rr * .42], 20, 160, fill=ink, width=e)
    if kind == "shield":
        sx0, sy0 = cx - rr * 1.5, cy - rr * .3
        d.polygon([(sx0, sy0 - rr * .7), (sx0 + rr * .78, sy0 - rr * .45), (sx0 + rr * .7, sy0 + rr * .6),
                   (sx0, sy0 + rr * 1.0), (sx0 - rr * .7, sy0 + rr * .6), (sx0 - rr * .78, sy0 - rr * .45)],
                  fill=(150, 200, 236), outline=INK, width=lw)
        d.line([(sx0, sy0 - rr * .5), (sx0, sy0 + rr * .7)], fill=(226, 244, 255), width=max(3, int(rad * .09)))
        d.line([(sx0 - rr * .45, sy0 + rr * .1), (sx0 + rr * .45, sy0 + rr * .1)], fill=(226, 244, 255), width=max(3, int(rad * .09)))
    if kind == "pearl":
        for k in range(3):
            a = t * 1.6 + k * 2.09
            px, py = cx + math.cos(a) * rr * 1.5, cy + math.sin(a) * rr * 1.15
            star(d, px, py, rr * .16, (255, 255, 255, 230))
    if kind == "cell":
        for k, (x0, y0, x1, y1) in enumerate([(-.5, -.3, -.1, .2), (.1, -.45, .35, 0), (-.2, .15, .2, .5)]):
            d.line([(cx + rr * x0, cy + rr * y0), (cx + rr * x1, cy + rr * y1)], fill=(214, 176, 170), width=max(2, int(rad * .05)))

def star(d, x, y, s, col):
    d.polygon([(x, y - s), (x + s * .28, y - s * .28), (x + s, y), (x + s * .28, y + s * .28),
               (x, y + s), (x - s * .28, y + s * .28), (x - s, y), (x - s * .28, y - s * .28)], fill=col)

# ---------------- エフェクト ----------------
def fx_sparkles(im, cx, cy, rad, t, n=9, col=(255, 246, 210, 230)):
    d = ImageDraw.Draw(im, "RGBA")
    for k in range(n):
        a = t * 1.3 + k * 6.283 / n
        rr = rad * (1.25 + 0.16 * math.sin(t * 2.2 + k))
        s = rad * (0.07 + 0.05 * (0.5 + 0.5 * math.sin(t * 3 + k)))
        star(d, cx + math.cos(a) * rr, cy + math.sin(a) * rr * .8, s, col)

def fx_rings(im, cx, cy, rad, t, col=(235, 92, 82)):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(3):
        ph = (t * .55 + k / 3.0) % 1.0
        rr = rad * (1.0 + ph * 1.5)
        a = int(150 * (1 - ph))
        d.ellipse([cx - rr, cy - rr * .92, cx + rr, cy + rr * .92], outline=col + (a,), width=14)
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(6)))

def fx_foam(im, cx, cy, t, n=26, seed=5, spread=340, top=-420):
    d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(seed)
    for i in range(n):
        x = cx + rnd.uniform(-spread, spread)
        y0 = cy + top + rnd.uniform(-160, 60)
        y = y0 + ((t * 210 + i * 47) % 620)
        rr = rnd.uniform(18, 52)
        a = int(220 * cl(1.3 - (y - y0) / 620))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, a), outline=(226, 232, 244, a), width=3)
        d.ellipse([x - rr * .5, y - rr * .6, x - rr * .05, y - rr * .1], fill=(255, 255, 255, a))

def fx_steam(im, cx, cy, t, seed=9):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rnd = random.Random(seed)
    for i in range(14):
        x = cx + rnd.uniform(-300, 300)
        y = cy + 160 - ((t * 90 + i * 37) % 420)
        rr = rnd.uniform(50, 120)
        d.ellipse([x - rr, y - rr * .7, x + rr, y + rr * .7], fill=(255, 255, 255, 120))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(26)))

def fx_zzz(im, cx, cy, t):
    d = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(FONT, 76)
    for k in range(3):
        ph = (t * .5 + k / 3.0) % 1.0
        a = int(230 * (1 - ph))
        d.text((cx + 40 + ph * 90, cy - 40 - ph * 200), "Z", font=f,
               fill=(120, 132, 190, a), stroke_width=6, stroke_fill=(255, 255, 255, a))

def fx_scar(im, cx, cy, alpha):
    """色素沈着っぽい影"""
    if alpha <= 0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for (x, y, rx, ry) in ((-70, 40, 78, 52), (60, -20, 62, 46), (10, 110, 54, 38)):
        d.ellipse([cx + x - rx, cy + y - ry, cx + x + rx, cy + y + ry],
                  fill=(150, 96, 92, int(150 * alpha)))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(24)))

def fx_pores(im, cx, cy, rad, tight, clog=0.0):
    """毛穴：tight=1で引き締まる / clog=1で詰まる"""
    d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(11)
    for i in range(26):
        a = rnd.uniform(0, 6.283)
        rr = rad * rnd.uniform(.62, .88)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        sz = lerp(13, 6, tight)
        col = clerp((198, 162, 156), (104, 80, 74), clog)
        d.ellipse([x - sz, y - sz, x + sz, y + sz], fill=col + (205,))

def cream_dab(im, x, y, s=1.0):
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse([x - 70 * s, y - 44 * s, x + 70 * s, y + 44 * s], fill=(255, 252, 248), outline=INK, width=4)
    d.ellipse([x - 40 * s, y - 66 * s, x + 34 * s, y - 6 * s], fill=(255, 255, 255), outline=INK, width=4)

def finger(im, x, y, s=1.0, ang=0.0):
    """つまもうとする指"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for sx in (-1, 1):
        cx = x + sx * 92 * s
        d.rounded_rectangle([cx - 56 * s, y - 330 * s, cx + 56 * s, y + 40 * s], 56 * s,
                            fill=(253, 231, 222), outline=INK, width=5)
        d.arc([cx - 34 * s, y - 34 * s, cx + 34 * s, y + 18 * s], 200, 340, fill=(232, 196, 188), width=5)
    im.alpha_composite(ov.rotate(ang, resample=Image.BICUBIC, center=(x, y)))

def mask_shape(im, cx, cy, s=1.0):
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([cx - 210 * s, cy - 130 * s, cx + 210 * s, cy + 130 * s], 60 * s,
                        fill=(250, 252, 255), outline=INK, width=5)
    for k in range(4):
        d.arc([cx - 210 * s, cy - 120 * s + k * 66 * s, cx + 210 * s, cy - 40 * s + k * 66 * s],
              10, 170, fill=(214, 224, 238), width=5)
    for sx in (-1, 1):
        ex = cx + sx * 232 * s
        d.arc([ex - 70 * s, cy - 78 * s, ex + 70 * s, cy + 78 * s],
              -80 if sx > 0 else 100, 80 if sx > 0 else 260, fill=INK, width=5)

def icon(im, kind, cx, cy, s=1.0, a=255):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    R = 92 * s
    d.rounded_rectangle([cx - R, cy - R, cx + R, cy + R], 34 * s, fill=(255, 255, 255, 232), outline=INK, width=5)
    if kind == "veg":
        d.polygon([(cx, cy + 52 * s), (cx - 40 * s, cy - 24 * s), (cx + 40 * s, cy - 24 * s)], fill=(240, 146, 66), outline=INK, width=4)
        d.ellipse([cx - 48 * s, cy - 62 * s, cx + 4 * s, cy - 14 * s], fill=(122, 186, 104), outline=INK, width=4)
        d.ellipse([cx - 6 * s, cy - 66 * s, cx + 46 * s, cy - 16 * s], fill=(140, 200, 118), outline=INK, width=4)
    elif kind == "moon":
        d.ellipse([cx - 52 * s, cy - 52 * s, cx + 52 * s, cy + 52 * s], fill=(250, 214, 110), outline=INK, width=4)
        d.ellipse([cx - 16 * s, cy - 64 * s, cx + 80 * s, cy + 40 * s], fill=(255, 255, 255, 255))
    elif kind == "umbrella":
        d.pieslice([cx - 62 * s, cy - 56 * s, cx + 62 * s, cy + 42 * s], 180, 360, fill=(238, 150, 176), outline=INK, width=4)
        d.line([(cx, cy - 8 * s), (cx, cy + 58 * s)], fill=INK, width=int(7 * s))
    elif kind == "sunscreen":
        d.rounded_rectangle([cx - 34 * s, cy - 26 * s, cx + 34 * s, cy + 58 * s], 14 * s, fill=(250, 244, 236), outline=INK, width=4)
        d.rounded_rectangle([cx - 16 * s, cy - 58 * s, cx + 16 * s, cy - 22 * s], 8 * s, fill=(246, 196, 96), outline=INK, width=4)
        d.line([(cx - 18 * s, cy + 6 * s), (cx + 18 * s, cy + 6 * s)], fill=(214, 200, 190), width=int(6 * s))
    elif kind == "drip":
        d.rounded_rectangle([cx - 34 * s, cy - 62 * s, cx + 34 * s, cy + 20 * s], 16 * s, fill=(226, 240, 250), outline=INK, width=4)
        d.rectangle([cx - 24 * s, cy - 30 * s, cx + 24 * s, cy + 18 * s], fill=(206, 230, 246))
        d.line([(cx, cy + 20 * s), (cx, cy + 62 * s)], fill=INK, width=int(6 * s))
    elif kind == "bottle":
        d.rounded_rectangle([cx - 38 * s, cy - 30 * s, cx + 38 * s, cy + 62 * s], 16 * s, fill=(238, 244, 252), outline=INK, width=4)
        d.rounded_rectangle([cx - 18 * s, cy - 62 * s, cx + 18 * s, cy - 26 * s], 8 * s, fill=(206, 220, 240), outline=INK, width=4)
        for k in range(3):
            d.line([(cx - 22 * s, cy + 2 * s + k * 16 * s), (cx + 22 * s, cy + 2 * s + k * 16 * s)], fill=(178, 192, 214), width=int(5 * s))
    elif kind == "calendar":
        d.rounded_rectangle([cx - 56 * s, cy - 48 * s, cx + 56 * s, cy + 56 * s], 12 * s, fill=(255, 255, 255), outline=INK, width=4)
        d.rectangle([cx - 56 * s, cy - 48 * s, cx + 56 * s, cy - 20 * s], fill=(238, 150, 150))
        for r_ in range(2):
            for c_ in range(4):
                d.rectangle([cx - 44 * s + c_ * 24 * s, cy - 6 * s + r_ * 26 * s,
                             cx - 28 * s + c_ * 24 * s, cy + 8 * s + r_ * 26 * s], fill=(228, 226, 232))
        d.line([(cx - 6 * s, cy + 22 * s), (cx + 6 * s, cy + 38 * s), (cx + 34 * s, cy - 6 * s)], fill=(226, 96, 96), width=int(9 * s))
    elif kind == "note":
        d.ellipse([cx - 52 * s, cy - 52 * s, cx + 52 * s, cy + 52 * s], fill=(250, 226, 150), outline=INK, width=4)
        d.line([(cx, cy - 28 * s), (cx, cy + 10 * s)], fill=INK, width=int(11 * s))
        d.ellipse([cx - 7 * s, cy + 22 * s, cx + 7 * s, cy + 36 * s], fill=INK)
    elif kind == "mask":
        d.rounded_rectangle([cx - 58 * s, cy - 36 * s, cx + 58 * s, cy + 36 * s], 18 * s, fill=(250, 252, 255), outline=INK, width=4)
        for k in range(3):
            d.arc([cx - 58 * s, cy - 30 * s + k * 20 * s, cx + 58 * s, cy + 2 * s + k * 20 * s], 10, 170, fill=(206, 218, 234), width=4)
    if a < 255:
        ov.putalpha(ov.getchannel("A").point(lambda v: int(v * a / 255)))
    im.alpha_composite(ov)

# ---------------- テロップ ----------------
def text_center(d, cx, y, s, font, alpha=255, stroke=8):
    bb = d.textbbox((0, 0), s, font=font, stroke_width=stroke)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), s, font=font, fill=(255, 255, 255, alpha),
           stroke_width=stroke, stroke_fill=(34, 24, 30, int(alpha * .9)))

def draw_telop(im, lines, subs, appear):
    a = int(255 * ease(cl(appear)))
    if a <= 0: return
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    top = 1250
    for y in range(top, H):
        k = (y - top) / (H - top)
        bd.line([(0, y), (W, y)], fill=(16, 12, 18, int(155 * (k ** 0.7) * a / 255)))
    im.alpha_composite(band)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rise = int(26 * (1 - ease(cl(appear))))
    fnt = F_TELOP if max(len(x) for x in lines) <= 13 else F_TELOP_S
    y = 1382 + rise
    for ln in lines:
        text_center(d, W / 2, y, ln, fnt, a)
        y += 100 if fnt is F_TELOP else 88
    y += 16
    for ln in subs:
        text_center(d, W / 2, y, ln, F_SUB, int(a * .95), stroke=5)
        y += 58
    im.alpha_composite(ov)

def draw_tag(im, title, t):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    a = int(255 * cl(t / 0.6))
    bb = d.textbbox((0, 0), title, font=F_TAG)
    w = bb[2] - bb[0] + 84
    d.rounded_rectangle([60, 92, 60 + w, 176], 42, fill=(28, 22, 26, int(a * .55)))
    d.text((102, 112), title, font=F_TAG, fill=(255, 255, 255, a))
    im.alpha_composite(ov)

def label(im, cx, y, s, a=255):
    if a <= 0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    text_center(ImageDraw.Draw(ov), cx, y, s, F_LABEL, a, stroke=6)
    im.alpha_composite(ov)
