#!/usr/bin/env python3
"""ショーリール用の15秒のBGMと効果音を合成する（120BPM、1小節=2秒でシーン転換と同期）。

    python3 score.py [出力先.wav]

numpy のみ使用。映像のカット（showreel.html の SCENES）と同じ秒数に音を置いている。
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 15.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM
rng = np.random.default_rng(2026)


def buf():
    return np.zeros(N)


def place(dst, sig, t, gain=1.0):
    i = int(round(t * SR))
    if i >= N:
        return
    j = min(N, i + len(sig))
    dst[i:j] += sig[: j - i] * gain


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lowpass(x, cutoff):
    """one-pole lowpass; cutoff may be an array (sweeps)."""
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def saw(freq, n, harmonics=24, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h in range(1, harmonics + 1):
        if freq * h > SR / 2.2:
            break
        out += np.sin(2 * np.pi * freq * h * (1 + detune) * t) / h
    return out * 0.6


# ---------------- instruments ----------------
def kick(strength=1.0):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 44 + 120 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.28)
    click = rng.standard_normal(n) * np.exp(-t / 0.003) * 0.35
    return np.tanh((body + click) * 1.6 * strength) * 0.9


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    x = highpass(rng.standard_normal(n), 7000)
    return x * env_exp(n, 0.07 if open_ else 0.014) * 0.5


def clap():
    n = int(0.35 * SR)
    x = rng.standard_normal(n)
    x = highpass(lowpass(x, 2600), 900)
    e = np.zeros(n)
    for k, d in enumerate([0, 0.011, 0.022]):
        i = int(d * SR)
        e[i:] += env_exp(n - i, 0.006 if k < 2 else 0.09)
    return x * e * 0.9


def pluck(m, dur=0.35, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    out = np.zeros(n)
    for h in range(1, 14):
        if f * h > SR / 2.2:
            break
        out += np.sin(2 * np.pi * f * h * t) / h * np.exp(-t * (6 + h * 5 / bright))
    return out * np.minimum(1, t / 0.002) * 0.5


def bell(m, dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    out = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9)
           + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.35)
           + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.12))
    return out * np.minimum(1, t / 0.001) * 0.35


def bass_note(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * saw(f, n, 8)
    e = np.minimum(1, t / 0.004) * np.exp(-t / (dur * 0.9))
    return np.tanh(x * 1.4) * e * 0.55


def pad(notes, dur, attack=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in notes:
        for d in (-0.004, 0.0, 0.0045):
            out += saw(midi(m), n, 10, d)
    out = lowpass(out, 1800)
    e = np.minimum(1, t / attack) * np.minimum(1, (dur - t) / 0.6).clip(0)
    return out * e * 0.07


def whoosh(dur, rise=True, peak=0.8):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    shape = t ** 2.2 if rise else (1 - t) ** 2
    x = rng.standard_normal(n)
    cutoff = 300 + 7000 * (t ** 1.5 if rise else (1 - t))
    x = lowpass(x, cutoff) - 0.6 * lowpass(x, cutoff * 0.3)
    return x * shape * peak


def riser(dur, f0=180, f1=1400):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    f = f0 * (f1 / f0) ** (t ** 1.8)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = sum(np.sin(ph * k * (1 + 0.003 * k)) / k for k in (1, 2, 3))
    return tone * t ** 2.5 * 0.18 + whoosh(dur, True, 0.5)


def impact(size=1.0):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    f = 32 + 70 * np.exp(-t / 0.08)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7)
    noise = lowpass(rng.standard_normal(n), 3000) * np.exp(-t / 0.18) * 0.5
    return np.tanh((sub + noise) * 1.8) * 0.8 * size


def tick(freq=3200):
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.004) * 0.35


def reverb(x, seconds=1.8, mix=1.0):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / (seconds / 6.9))
    ir = lowpass(ir, 5000)
    ir[: int(0.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return y * mix


# ---------------- arrangement ----------------
drums, bass, music, fx, send = buf(), buf(), buf(), buf(), buf()
kick_env = buf()

# chords per bar (2s): Dm, Bb, F, C, Dm, Bb, C -> F
ROOTS = {2: 38, 4: 34, 6: 41, 8: 36, 10: 38, 12: 34}
CHORDS = {2: [62, 65, 69, 72], 4: [58, 62, 65, 69], 6: [60, 65, 69, 72], 8: [60, 64, 67, 72], 10: [62, 65, 69, 74], 12: [58, 62, 65, 70]}

# intro 0-2: line tick, fold boom, scramble ticks, whoosh into the drop
place(fx, tick(2400), 0.02, 0.9)
place(fx, whoosh(0.4, False, 0.35), 0.02)
place(fx, impact(0.55), 0.44)
for i, m in enumerate([74, 77, 81, 84, 86, 89]):
    place(send, bell(m, 1.2), 0.62 + i * 0.07, 0.35)
for i in range(10):
    place(fx, tick(2800 + (i % 3) * 600), 0.9 + i * 0.05, 0.25)
place(music, pad([62, 65, 69], 2.0, 0.6), 0.0, 0.8)
place(fx, riser(0.9, 200, 1800), 1.1, 0.9)

# groove 2-12
k = kick()
for b in range(int((13.5 - 2.0) / BEAT)):
    t = 2.0 + b * BEAT
    place(drums, k, t, 1.0 if b % 4 == 0 else 0.85)
    place(kick_env, env_exp(int(0.3 * SR), 0.09), t)
    place(drums, hat(open_=(b % 4 == 3)), t + BEAT / 2, 0.5)
    if b % 2 == 1:
        place(drums, clap(), t, 0.55)
        place(send, clap(), t, 0.25)
    for s in (1, 3):
        place(drums, hat(), t + s * BEAT / 4, 0.18)

for bar, root in ROOTS.items():
    end = min(bar + 2, 13.5)
    steps = int((end - bar) / (BEAT / 2))
    for s in range(steps):
        m = root + (12 if s % 4 == 3 else 0)
        place(bass, bass_note(m, BEAT / 2 * 0.92), bar + s * BEAT / 2)
    chord = CHORDS[bar]
    place(music, pad(chord, end - bar + 0.4, 0.05), bar, 1.0)
    # 16th arpeggio
    pattern = [0, 1, 2, 3, 2, 1, 3, 0]
    for s in range(int((end - bar) / (BEAT / 4))):
        m = chord[pattern[s % 8]] + (12 if (s // 8) % 2 else 0)
        acc = 1.0 if s % 4 == 0 else 0.6
        place(music, pluck(m, 0.3, 1.4 if bar >= 8 else 1.0), bar + s * BEAT / 4, 0.28 * acc)
        place(send, pluck(m, 0.3), bar + s * BEAT / 4, 0.1 * acc)

# transitions
for t0, d in ((3.5, 0.5), (5.6, 0.4), (7.7, 0.3), (9.75, 0.25), (11.6, 0.4)):
    place(fx, whoosh(d, True, 0.55), t0)
for t0 in (2.0, 6.0, 10.0, 12.0):
    place(fx, impact(0.6), t0)
    place(drums, hat(True), t0, 0.5)
# media cuts: a stab per cut + the 50+ hit
for i in range(8):
    place(fx, tick(1800 + i * 180), 8.0 + i * 0.125, 0.5)
    place(send, pluck(CHORDS[8][i % 4] + 12, 0.25, 2.0), 8.0 + i * 0.125, 0.25)
place(fx, impact(0.7), 9.0)
place(fx, whoosh(0.3, False, 0.4), 9.0)
# award sparkle
for i, m in enumerate([86, 89, 93, 98, 93, 101]):
    place(send, bell(m, 1.4), 10.02 + i * 0.09, 0.3)
place(send, bell(74, 2.0), 10.85, 0.5)
# mosaic flips
for i in range(9):
    place(fx, tick(2200 + i * 150), 12.0 + i * 0.035, 0.3)

# outro: dive riser, final hit, resolve on F
place(fx, riser(0.55, 150, 2400), 12.95, 1.0)
place(fx, impact(1.1), 13.5)
place(drums, kick(1.3), 13.5, 1.0)
place(send, pad([53, 60, 65, 69, 72, 77], 1.5, 0.02), 13.5, 1.6)
place(music, pad([41, 53, 60, 65, 69], 1.5, 0.02), 13.5, 1.2)
place(send, bell(77, 1.5), 13.5, 0.6)
place(send, bell(84, 1.5), 13.56, 0.35)
for i in range(16):
    place(fx, tick(3400 + (i % 4) * 300), 14.1 + i * 0.025, 0.18)

# ---------------- mix ----------------
duck = 1 - 0.6 * np.clip(lowpass(kick_env, 40) * 1.4, 0, 1)
bass = lowpass(bass, 900) * duck
music = music * (0.35 + 0.65 * duck)
wet = reverb(send + music * 0.25 + fx * 0.15, 1.9)

L = drums * 0.9 + bass + music + fx * 0.8 + wet * 0.5
d = int(0.011 * SR)
music_r = np.concatenate([np.zeros(d), music[:-d]])
wet_r = np.concatenate([np.zeros(d * 2), wet[: -d * 2]])
R = drums * 0.9 + bass + music_r + fx * 0.8 + wet_r * 0.5
st = np.stack([L, R], axis=1)

fade = np.ones(N)
fade[-int(0.25 * SR):] = np.linspace(1, 0, int(0.25 * SR)) ** 2
st *= fade[:, None]
st = np.tanh(st / np.max(np.abs(st)) * 1.6)
st = st / np.max(np.abs(st)) * 0.89

out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent / '../exports/showreel/audio.wav')
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('wrote', out)
