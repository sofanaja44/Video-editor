"""Frame effects: easing, colour grade, rain, bloom, glitch, speed lines, lightning..."""
import math

import cv2
import numpy as np


# ---------------------------------------------------------------- easing / envelopes
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


def ease_in_cubic(p):
    p = clamp(p)
    return p ** 3


def ease_in_out(p):
    p = clamp(p)
    return 3 * p * p - 2 * p * p * p


def ease_out_expo(p):
    p = clamp(p)
    return 1 if p >= 1 else 1 - 2 ** (-10 * p)


def back_out(p, s=2.2):
    p = clamp(p)
    return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2


def bounce_out(p):
    p = clamp(p)
    n, d = 7.5625, 2.75
    if p < 1 / d:
        return n * p * p
    if p < 2 / d:
        p -= 1.5 / d
        return n * p * p + 0.75
    if p < 2.5 / d:
        p -= 2.25 / d
        return n * p * p + 0.9375
    p -= 2.625 / d
    return n * p * p + 0.984375


def spring(u, freq=3.2, decay=5.0):
    """Damped oscillation starting at 1 and settling to 0."""
    if u < 0:
        return 0.0
    return math.exp(-decay * u) * math.cos(2 * math.pi * freq * u)


def punch(t, t0, rise=0.05, decay=0.3):
    """Fast attack, exponential release."""
    u = t - t0
    if u < 0:
        return 0.0
    if u < rise:
        return math.sin(0.5 * math.pi * u / rise)
    return math.exp(-(u - rise) / decay)


def window(t, a, b, fade_in=0.1, fade_out=0.1):
    if t < a or t > b:
        return 0.0
    return min(clamp((t - a) / fade_in) if fade_in else 1, clamp((b - t) / fade_out) if fade_out else 1)


def wobble(t, seed=0.0):
    """Smooth pseudo-random signal in roughly [-1, 1]."""
    return (math.sin(t * 13.1 + seed) + 0.6 * math.sin(t * 7.3 + 1.7 * seed + 1.2)
            + 0.35 * math.sin(t * 23.9 + 2.3 * seed + 2.1)) / 1.95


# ---------------------------------------------------------------- colour
def _grade_luts():
    x = np.arange(256, dtype=np.float32) / 255
    k = 2.1
    s = 0.5 + 0.5 * np.tanh(k * (x - 0.5)) / math.tanh(k * 0.5)
    c = 0.5 * s + 0.5 * x
    r = np.clip(c * 1.01 + 0.005, 0, 1)
    g = np.clip(c * 1.0 + 0.005, 0, 1)
    b = np.clip(c * 0.93 + 0.07 * (1 - c) ** 2, 0, 1)
    return [(ch * 255).astype(np.uint8) for ch in (r, g, b)]


_LUTS = _grade_luts()


def grade(img, saturation=1.2, brightness=1.0):
    """Teal shadows / warm highlights, gentle S-curve and saturation boost (uint8 RGB)."""
    out = np.dstack([cv2.LUT(img[..., i], _LUTS[i]) for i in range(3)]).astype(np.float32)
    gray = out.mean(axis=2, keepdims=True)
    out = gray + (out - gray) * saturation
    out *= brightness
    return np.clip(out, 0, 255).astype(np.uint8)


def vignette(w, h, strength=0.55):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / math.sqrt(2)
    return (1 - strength * np.clip(r, 0, 1) ** 2.2)[..., None].astype(np.float32)


def grain_bank(w, h, n=6, amount=0.035, seed=7):
    rng = np.random.default_rng(seed)
    bank = []
    for _ in range(n):
        g = rng.standard_normal((h // 2, w // 2)).astype(np.float32) * amount
        bank.append(cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)[..., None])
    return bank


def bloom(frame, amount=0.4, threshold=0.62):
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    bright = np.clip((small - threshold) / (1 - threshold), 0, 1)
    glow = cv2.GaussianBlur(bright, (0, 0), 9) + cv2.GaussianBlur(bright, (0, 0), 22) * 0.8
    frame += cv2.resize(glow, (w, h), interpolation=cv2.INTER_LINEAR) * amount


def flash(frame, color, amount):
    if amount <= 0.003:
        return
    frame *= 1 - amount
    frame += np.array(color, np.float32) * amount


def chroma_split(frame, px):
    px = int(round(px))
    if px == 0:
        return
    r = frame[..., 0].copy()
    b = frame[..., 2].copy()
    frame[..., 0] = np.roll(r, px, axis=1)
    frame[..., 2] = np.roll(b, -px, axis=1)


def glitch(frame, amount, seed):
    """Horizontal slice displacement + RGB split + occasional colour-inverted band."""
    if amount <= 0.01:
        return
    rng = np.random.default_rng(seed)
    h, w = frame.shape[:2]
    chroma_split(frame, 22 * amount * rng.uniform(0.5, 1.0) * rng.choice([-1, 1]))
    for _ in range(int(4 + 10 * amount)):
        y = rng.integers(0, h - 10)
        bh = int(rng.integers(6, int(20 + 110 * amount)))
        shift = int(rng.normal(0, 70 * amount))
        frame[y:y + bh] = np.roll(frame[y:y + bh], shift, axis=1)
        if rng.random() < 0.18 * amount:
            frame[y:y + bh] = 1 - frame[y:y + bh]
        elif rng.random() < 0.25:
            frame[y:y + bh] = frame[y:y + bh][..., [2, 0, 1]]


def motion_blur(frame, px, vertical=False):
    px = int(px)
    if px < 3:
        return frame
    k = (1, px) if vertical else (px, 1)
    return cv2.blur(frame, k)


def scanlines(frame, amount):
    if amount <= 0:
        return
    frame[::4] *= 1 - amount


# ---------------------------------------------------------------- particles / overlays
class Rain:
    """Deterministic rain streaks: the layout only depends on time t."""

    def __init__(self, w, h, n=320, seed=11, angle_deg=12):
        rng = np.random.default_rng(seed)
        self.w, self.h = w, h
        self.x0 = rng.uniform(-200, w + 200, n)
        self.y0 = rng.uniform(0, h, n)
        self.depth = rng.uniform(0, 1, n) ** 1.6          # 0 far .. 1 near
        self.speed = 1300 + 2400 * self.depth
        self.length = 28 + 120 * self.depth
        self.alpha = 0.10 + 0.45 * self.depth
        self.thick = (1 + 3 * self.depth).astype(int)
        self.order = rng.permutation(n)
        a = math.radians(angle_deg)
        self.dx, self.dy = math.sin(a), math.cos(a)

    def render(self, t, intensity):
        layer = np.zeros((self.h, self.w), np.uint8)
        count = int(len(self.order) * clamp(intensity, 0, 1))
        span = self.h + 300
        for i in self.order[:count]:
            travel = (self.y0[i] + self.speed[i] * t) % span - 150
            x = self.x0[i] + travel * self.dx / self.dy
            y = travel
            L = self.length[i]
            p1 = (int(x), int(y))
            p2 = (int(x - L * self.dx), int(y - L * self.dy))
            cv2.line(layer, p2, p1, int(255 * self.alpha[i]), int(self.thick[i]), cv2.LINE_AA)
        return cv2.GaussianBlur(layer, (0, 0), 1.2).astype(np.float32) / 255.0


def apply_rain(frame, layer, amount):
    if amount <= 0.01:
        return
    tint = np.array([0.85, 0.93, 1.0], np.float32)
    frame += layer[..., None] * tint * amount


def speed_lines(w, h, cx, cy, seed, amount, inner=380, count=70):
    """Anime style radial speed lines. Returns a float32 alpha layer."""
    layer = np.zeros((h // 2, w // 2), np.uint8)
    rng = np.random.default_rng(seed)
    R = math.hypot(w, h) / 2
    for _ in range(count):
        ang = rng.uniform(0, 2 * math.pi)
        width = rng.uniform(0.004, 0.018)
        r0 = inner * rng.uniform(0.9, 1.6)
        pts = np.array([
            (cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)),
            (cx + R * 1.2 * math.cos(ang - width), cy + R * 1.2 * math.sin(ang - width)),
            (cx + R * 1.2 * math.cos(ang + width), cy + R * 1.2 * math.sin(ang + width)),
        ]) / 2
        cv2.fillPoly(layer, [pts.astype(np.int32)], int(255 * rng.uniform(0.35, 1.0)), cv2.LINE_AA)
    layer = cv2.resize(layer, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    return layer * amount


def lightning_layer(w, h, seed, start=(0.62, 0.0), end=(0.38, 0.42)):
    """Jagged glowing bolt (midpoint displacement) with a couple of branches."""
    rng = np.random.default_rng(seed)

    def bolt(p, q, disp, depth):
        if depth == 0:
            return [p, q]
        mx = (p[0] + q[0]) / 2 + rng.normal(0, disp)
        my = (p[1] + q[1]) / 2 + rng.normal(0, disp * 0.3)
        return bolt(p, (mx, my), disp / 2, depth - 1)[:-1] + bolt((mx, my), q, disp / 2, depth - 1)

    core = np.zeros((h, w), np.uint8)
    p, q = (start[0] * w, start[1] * h), (end[0] * w, end[1] * h)
    main = bolt(p, q, w * 0.12, 7)
    cv2.polylines(core, [np.array(main, np.int32)], False, 255, 7, cv2.LINE_AA)
    for _ in range(3):
        a = main[rng.integers(len(main) // 4, len(main) * 3 // 4)]
        b = (a[0] + rng.normal(0, w * 0.18), a[1] + rng.uniform(h * 0.06, h * 0.16))
        cv2.polylines(core, [np.array(bolt(a, b, w * 0.05, 5), np.int32)], False, 200, 3, cv2.LINE_AA)
    core = core.astype(np.float32) / 255
    glow = cv2.GaussianBlur(core, (0, 0), 14) * 2.2 + cv2.GaussianBlur(core, (0, 0), 40) * 1.5
    return core, glow


def light_leak(w, h, t, amount, palette=((1.0, 0.5, 0.18), (0.35, 0.55, 1.0))):
    """Two drifting soft colour blobs (additive)."""
    if amount <= 0.01:
        return None
    sw, sh = w // 8, h // 8
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    out = np.zeros((sh, sw, 3), np.float32)
    for i, col in enumerate(palette):
        cx = sw * (0.15 + 0.7 * (0.5 + 0.5 * math.sin(t * 0.9 + i * 2.4)))
        cy = sh * (0.1 + 0.25 * i + 0.1 * math.sin(t * 0.7 + i))
        r = sw * (0.55 + 0.15 * math.sin(t * 1.3 + i))
        blob = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))[..., None]
        out += blob * np.array(col, np.float32)
    return cv2.resize(out, (w, h), interpolation=cv2.INTER_LINEAR) * amount


def vertical_gradient(w, h, y0, y1, peak_y, strength):
    ys = np.arange(h, dtype=np.float32)
    g = np.where(ys < peak_y, (ys - y0) / max(peak_y - y0, 1), (y1 - ys) / max(y1 - peak_y, 1))
    g = np.clip(g, 0, 1) ** 0.8 * strength
    return g[:, None, None].astype(np.float32)
