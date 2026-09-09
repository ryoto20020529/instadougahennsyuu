# -*- coding: utf-8 -*-
"""BGMをその場で合成する（オリジナル・権利フリー）。
やさしいオルゴール風メロディ＋パッド＋軽いリズムの、かわいい系ローファイ。"""
import numpy as np, wave, os, math

SR = 48000

def _env(n, a, d, s, r, sus=0.7):
    """ADSR エンベロープ"""
    a, d, r = max(1, int(a * SR)), max(1, int(d * SR)), max(1, int(r * SR))
    s = max(0, n - a - d - r)
    e = np.concatenate([
        np.linspace(0, 1, a), np.linspace(1, sus, d),
        np.full(s, sus), np.linspace(sus, 0, r)])
    return np.pad(e, (0, max(0, n - len(e))))[:n]

def _hz(midi): return 440.0 * 2 ** ((midi - 69) / 12.0)

def _add(buf, sig, at):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[:j - i]

def _bell(midi, dur, amp):
    """オルゴール（サイン＋倍音、速い減衰）"""
    n = int(dur * SR); t = np.arange(n) / SR
    f = _hz(midi)
    env = np.exp(-t * 4.2)
    s = (np.sin(2 * np.pi * f * t) * 1.0
         + np.sin(2 * np.pi * f * 2 * t) * 0.34
         + np.sin(2 * np.pi * f * 3.01 * t) * 0.12
         + np.sin(2 * np.pi * f * 5.4 * t) * 0.05)
    atk = np.minimum(1.0, t * 400)
    return s * env * atk * amp

def _pad(midis, dur, amp):
    """やわらかいパッド（微妙にデチューンした三角波っぽい音）"""
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for m in midis:
        for det in (-0.06, 0.0, 0.07):
            f = _hz(m + det)
            s += (np.sin(2 * np.pi * f * t)
                  + 0.18 * np.sin(2 * np.pi * 2 * f * t)
                  + 0.06 * np.sin(2 * np.pi * 3 * f * t))
    s /= (len(midis) * 3)
    vib = 1 + 0.02 * np.sin(2 * np.pi * 0.3 * t)
    return s * _env(n, 0.9, 0.5, 0, 1.1, .75) * vib * amp

def _bass(midi, dur, amp):
    n = int(dur * SR); t = np.arange(n) / SR
    f = _hz(midi)
    s = np.sin(2 * np.pi * f * t) + 0.12 * np.sin(2 * np.pi * 2 * f * t)
    return s * _env(n, 0.02, 0.25, 0, 0.5, .5) * amp

def _kick(amp):
    n = int(0.16 * SR); t = np.arange(n) / SR
    f = 110 * np.exp(-t * 22) + 46
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 15) * amp

def _hat(amp, rng):
    n = int(0.05 * SR); t = np.arange(n) / SR
    return rng.normal(0, 1, n) * np.exp(-t * 90) * amp

def _lowpass(x, cut=6200):
    a = math.exp(-2 * math.pi * cut / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(0, len(x), 1 << 16):          # ブロック処理
        blk = x[i:i + (1 << 16)]
        out = np.empty_like(blk)
        for j, v in enumerate(blk):
            acc = (1 - a) * v + a * acc
            out[j] = acc
        y[i:i + len(blk)] = out
    return y

def _reverb(x, amount=0.26):
    """簡易リバーブ（複数タップのディレイ）"""
    y = x.copy()
    for dly, g in ((0.061, .34), (0.089, .26), (0.127, .19), (0.181, .13)):
        d = int(dly * SR)
        y[d:] += x[:-d] * g * amount * 2.2
    return y

# I - V - vi - IV （キーは話数でずらす）
PROG = [(0, [0, 4, 7]), (7, [7, 11, 14]), (9, [9, 12, 16]), (5, [5, 9, 12])]
PENTA = [0, 2, 4, 7, 9, 12, 14, 16]

def make(seconds=50.0, seed=1, bpm=84, key=60, amp=1.0):
    rng = np.random.default_rng(seed)
    key = key + (seed * 2) % 5          # 話ごとにキーを少しずらす
    beat = 60.0 / bpm
    bar = beat * 4
    n = int((seconds + 2) * SR)
    pad = np.zeros(n); bell = np.zeros(n); bass = np.zeros(n); drum = np.zeros(n)
    nbars = int(seconds / bar) + 2
    for b in range(nbars):
        t0 = b * bar
        root, chord = PROG[b % 4]
        _add(pad, _pad([key + root - 12 + c for c in chord], bar * 1.02, 0.115), t0)
        _add(bass, _bass(key + root - 24, bar * .9, 0.16), t0)
        if b >= 1:                       # メロディは2小節目から
            for k in range(8):
                if rng.random() < 0.42: continue
                deg = PENTA[rng.integers(0, len(PENTA))]
                oct_ = 12 if rng.random() < 0.5 else 0
                _add(bell, _bell(key + root + deg + oct_, beat * 1.6,
                                 0.115 * (0.7 + 0.5 * rng.random())), t0 + k * beat / 2)
        for k in (0, 2):
            _add(drum, _kick(0.20), t0 + k * beat)
        for k in range(8):
            if k % 2 == 1:
                _add(drum, _hat(0.030, rng), t0 + k * beat / 2)
    mix = pad + bell * 0.9 + bass + drum
    mix = _lowpass(mix, 7000)
    mix = _reverb(mix, 0.3)
    mix = mix[:int(seconds * SR)]
    # フェード
    fi, fo = int(1.2 * SR), int(1.6 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)
    peak = np.max(np.abs(mix)) or 1.0
    mix = np.tanh(mix / peak * 1.15) * 0.85 * amp
    return mix

def save(path, seconds=50.0, seed=1):
    x = make(seconds, seed)
    st = np.stack([x, x], axis=1)                      # ステレオ
    st[:, 0] *= 0.97; st[:, 1] *= 1.0                  # ほんの少し広がりを
    data = (np.clip(st, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(path, "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data)
    return path

if __name__ == "__main__":
    import sys
    save(sys.argv[1] if len(sys.argv) > 1 else "bgm_test.wav", 50.0, int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    print("ok")
