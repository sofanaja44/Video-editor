"""Procedurally synthesised sound effects and the final audio mix."""
import numpy as np
from scipy import signal

SR = 44100


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _rng(seed):
    return np.random.default_rng(seed)


def _sweep_tone(f0, f1, dur, curve="exp"):
    t = _t(dur)
    if curve == "exp":
        f = f0 * (f1 / f0) ** (t / dur)
    else:
        f = f0 + (f1 - f0) * t / dur
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def _shaped_noise(dur, centers, width=0.5, seed=0):
    """Noise whose spectral centre follows `centers` (Hz, sampled across the duration)."""
    noise = _rng(seed).standard_normal(int(dur * SR) + 2048)
    f, tt, Z = signal.stft(noise, SR, nperseg=1024)
    track = np.interp(np.linspace(0, 1, Z.shape[1]), np.linspace(0, 1, len(centers)), centers)
    logf = np.log2(np.maximum(f, 20))[:, None]
    mask = np.exp(-((logf - np.log2(track)[None, :]) ** 2) / (2 * width ** 2))
    _, out = signal.istft(Z * mask, SR, nperseg=1024)
    out = out[:int(dur * SR)]
    return out / (np.abs(out).max() + 1e-9)


def whoosh(dur=0.45, seed=1):
    t = _t(dur)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return _shaped_noise(dur, [400, 2600, 900], 0.7, seed) * env


def riser(dur=0.5, seed=2):
    t = _t(dur)
    env = (t / dur) ** 2
    return _shaped_noise(dur, [250, 1200, 6000], 0.6, seed) * env


def impact(dur=0.8, seed=3):
    t = _t(dur)
    boom = _sweep_tone(120, 38, dur) * np.exp(-t * 5.0)
    click = _shaped_noise(dur, [3000, 800, 300], 1.0, seed) * np.exp(-t * 28)
    return np.tanh(1.6 * (boom * 0.9 + click * 0.6))


def pop(dur=0.09):
    t = _t(dur)
    return _sweep_tone(1300, 420, dur) * np.exp(-t * 45)


def thunder(dur=1.8, seed=4):
    t = _t(dur)
    crack = _shaped_noise(dur, [2500, 900], 1.0, seed) * np.exp(-t * 14)
    brown = np.cumsum(_rng(seed + 1).standard_normal(len(t)))
    brown = signal.sosfilt(signal.butter(2, [30, 260], "bandpass", fs=SR, output="sos"), brown)
    brown /= np.abs(brown).max() + 1e-9
    rumble_env = (1 - np.exp(-t * 18)) * np.exp(-t * 1.6) * (0.75 + 0.25 * np.sin(2 * np.pi * 5.3 * t))
    return np.tanh(1.4 * (crack * 0.7 + brown * rumble_env * 1.2))


def glitch(dur=0.2, seed=5):
    rng = _rng(seed)
    out = np.zeros(int(dur * SR))
    pos = 0
    while pos < len(out):
        n = int(rng.uniform(0.012, 0.03) * SR)
        f = rng.uniform(150, 2200)
        seg = np.sign(np.sin(2 * np.pi * f * np.arange(n) / SR))
        if rng.random() < 0.4:
            seg = np.round(rng.standard_normal(n) * 3) / 3
        out[pos:pos + n] = seg[:len(out) - pos] * rng.uniform(0.3, 0.8)
        pos += n
    return out


def slip(dur=0.5):
    """Cartoon 'wheee-oop' slide whistle."""
    t = _t(dur)
    half = dur * 0.55
    f = np.where(t < half, 320 * (1500 / 320) ** (t / half),
                 1500 * (180 / 1500) ** ((t - half) / (dur - half)))
    f *= 1 + 0.03 * np.sin(2 * np.pi * 11 * t)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.clip(t / 0.02, 0, 1) * np.clip((dur - t) / 0.08, 0, 1)
    return tone * env * 0.8


def gulp():
    """'Glek' – two low bloops."""
    one = _sweep_tone(210, 80, 0.11) * np.exp(-_t(0.11) * 20)
    out = np.zeros(int(0.26 * SR))
    out[:len(one)] += one
    out[int(0.13 * SR):int(0.13 * SR) + len(one)] += one * 0.8
    return out


def sparkle(seed=6):
    rng = _rng(seed)
    out = np.zeros(int(0.7 * SR))
    for i, f in enumerate([2093, 2637, 3136, 4186]):
        start = int(i * 0.06 * SR)
        t = _t(0.45)
        tone = np.sin(2 * np.pi * f * t) * np.exp(-t * 9) * rng.uniform(0.5, 0.9)
        out[start:start + len(t)] += tone[:len(out) - start]
    return out


def rain_bed(dur, seed=8):
    noise = _rng(seed).standard_normal(int(dur * SR))
    sos = signal.butter(2, [900, 7000], "bandpass", fs=SR, output="sos")
    return signal.sosfilt(sos, noise) * 0.35


SYNTHS = {
    "whoosh": whoosh, "riser": riser, "impact": impact, "pop": pop, "thunder": thunder,
    "glitch": glitch, "slip": slip, "gulp": gulp, "sparkle": sparkle,
}


def echo_tail(clip, dur, delay=0.22, feedback=0.55):
    """Feedback echo of `clip` that rings out over `dur` seconds."""
    out = np.zeros((int(dur * SR), clip.shape[1]))
    step = int(delay * SR)
    gain, pos = feedback, step
    while gain > 0.02 and pos < len(out):
        n = min(len(clip), len(out) - pos)
        out[pos:pos + n] += clip[:n] * gain
        gain *= feedback
        pos += step
    return out


def mix(source, events, total, end_card=False):
    """source: (n, 2) float array at SR; events: [(time, name, gain, pan)]; total seconds."""
    out = np.zeros((int(total * SR) + SR, 2))
    n = min(len(source), len(out))
    src = source[:n].copy()
    fade = int(0.12 * SR)
    src[-fade:] *= np.linspace(1, 0, fade)[:, None]
    out[:n] += src
    if end_card:
        # echo the last beat of the music into the end card
        clip = source[n - int(0.5 * SR):n] * np.hanning(int(0.5 * SR))[:, None]
        tail = echo_tail(clip, total - n / SR + 0.5)
        out[n:n + len(tail)] += tail[:len(out) - n]
        bed = rain_bed(total - n / SR, seed=9)
        bed *= np.clip(np.arange(len(bed)) / (0.3 * SR), 0, 1) * 0.25
        out[n:n + len(bed)] += bed[:, None]
    for i, (time, name, gain, pan) in enumerate(events):
        fn = SYNTHS[name]
        try:
            snd = fn(seed=20 + i)
        except TypeError:
            snd = fn()
        snd = snd * gain
        start = int(time * SR)
        end = min(len(out), start + len(snd))
        left, right = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
        out[start:end, 0] += snd[:end - start] * left * 1.41
        out[start:end, 1] += snd[:end - start] * right * 1.41
    out = out[:int(total * SR)]
    # simple fade-out at the very end
    tail = int(0.25 * SR)
    out[-tail:] *= np.linspace(1, 0, tail)[:, None]
    return out
