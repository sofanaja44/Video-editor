"""Motion-graphics edit of input/source.mp4 ("musim hujan" vlog).

Usage:
    python render.py                    # full render -> output/musim_hujan_motion.mp4
    python render.py --preview 2.4 5.5  # render single frames to output/preview/
"""
import argparse
import math
import subprocess
import sys
import wave
from multiprocessing import get_context
from pathlib import Path

import cv2
import numpy as np

from motion import fx, sfx
from motion.fx import back_out, clamp, ease_in_cubic, ease_out_cubic, ease_out_expo, punch, spring, window, wobble
from motion.text import (badge_sprite, blit, comic_burst_sprite, emoji_sprite, hazard_tape_sprite,
                         starburst_sprite, text_sprite, warning_sign_sprite)

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "input" / "source.mp4"
OUT = ROOT / "output" / "musim_hujan_motion.mp4"

# OpenCV's own thread pool does not survive fork(); the worker pool provides the parallelism.
cv2.setNumThreads(1)

FPS = 30
SW, SH = 576, 1024            # source size
W, H = 1080, 1920             # output size
SRC_FRAMES = 442
SRC_END = SRC_FRAMES / FPS    # 14.733 s
END_CARD = 2.0
TOTAL = SRC_END + END_CARD
N_FRAMES = int(round(TOTAL * FPS))

CYAN = "#2EE6FF"
YELLOW = "#FFD60A"
PINK = "#FF3D7F"
WHITE = "#FFFFFF"

# Burned-in TikTok captions (frame ranges, measured from the source) that get painted out.
SUB_FRAMES = [(38, 87), (104, 128), (137, 207), (250, 277), (328, 363), (376, 428)]

# Music beats (librosa, ~129 BPM) used for pulses in the music part of the clip.
BEATS = [6.97, 7.41, 7.87, 8.34, 8.80, 9.24, 9.68, 10.15, 10.61, 11.05, 11.52, 11.98,
         12.49, 12.98, 13.44, 13.91, 14.40]


# ======================================================================= captions
class Word:
    def __init__(self, text, t0, font="black", size=80, fill=WHITE, anim="pop", hl=True,
                 loop=None, glow=None, stroke=None):
        self.text, self.t0, self.anim, self.loop = text, t0, anim, loop
        stroke = stroke if stroke is not None else max(6, size // 10)
        self.spr = text_sprite(text, font, size, fill, stroke=stroke, glow=glow)
        self.spr_hl = text_sprite(text, font, size, YELLOW, stroke=stroke, glow=glow) if hl else None
        self.x = self.y = 0.0


class Block:
    """A group of caption lines; words pop in at their own time and leave together."""

    def __init__(self, lines, cy, t_end, line_gap=4, max_w=980, out_dur=0.16):
        self.lines, self.t_end, self.out_dur = lines, t_end, out_dur
        self.words = [w for line in lines for w in line]
        self.t_start = min(w.t0 for w in self.words)
        heights = [max(w.spr.ink_h for w in line) for line in lines]
        total_h = sum(heights) + line_gap * (len(lines) - 1)
        y = cy - total_h / 2
        for line, lh in zip(lines, heights):
            gap = max(22, 0.3 * lh)
            widths = [w.spr.ink_w for w in line]
            lw = sum(widths) + gap * (len(line) - 1)
            fit = min(1.0, max_w / lw)
            x = W / 2 - lw * fit / 2
            for w, ww in zip(line, widths):
                w.x, w.y, w.fit = x + ww * fit / 2, y + lh / 2, fit
                x += (ww + gap) * fit
            y += lh + line_gap
        order = sorted(self.words, key=lambda w: w.t0)
        for a, b in zip(order, order[1:] + [None]):
            a.t_next = b.t0 if b else t_end

    def draw(self, frame, t):
        if t < self.t_start - 0.01 or t > self.t_end + self.out_dur:
            return
        q = clamp((t - self.t_end) / self.out_dur)
        for w in self.words:
            u = t - w.t0
            if u < 0:
                continue
            dx = dy = rot = 0.0
            s, a = w.fit, clamp(u / 0.07)
            if w.anim == "pop":
                s *= 0.25 + 0.75 * back_out(u / 0.24)
                dy += 26 * (1 - ease_out_cubic(u / 0.24))
            elif w.anim == "drop":
                dy -= 200 * (1 - fx.bounce_out(u / 0.32))
                s *= 1 + 0.12 * max(0.0, spring(u - 0.3, 4, 7))
            elif w.anim == "stamp":
                p = u / 0.15
                s *= 1 + 1.7 * (1 - ease_out_cubic(p))
                a = clamp(u / 0.05)
                if p >= 1:
                    s *= 1 + 0.08 * spring(u - 0.15, 5, 9)
            elif w.anim == "slip":
                dx -= 700 * (1 - ease_out_expo(u / 0.22))
                k = spring(u - 0.18, 2.6, 4.2)
                rot -= 14 * k if u > 0.18 else 0
                dx += 50 * k if u > 0.18 else 0
                dy += 18 * abs(k) if u > 0.18 else 0
            elif w.anim == "slide":
                dx += 520 * (1 - ease_out_expo(u / 0.28))
                a = clamp(u / 0.12)
            if w.loop == "shake":
                dx += 7 * wobble(t * 3.2, w.t0)
                dy += 6 * wobble(t * 3.7, w.t0 + 4)
            elif w.loop == "wobble":
                rot += 6 * math.sin(2 * math.pi * 2.4 * u)
                s *= 1 + 0.04 * math.sin(2 * math.pi * 4.8 * u)
            elif w.loop == "float":
                dy += 7 * math.sin(2 * math.pi * 1.3 * u)
            active = w.t0 <= t < w.t_next
            spr = w.spr_hl if (active and w.spr_hl is not None) else w.spr
            if active:
                s *= 1 + 0.07 * ease_out_cubic(u / 0.12)
            if q > 0:
                s *= 1 - 0.55 * ease_in_cubic(q)
                dy -= 50 * ease_in_cubic(q)
                a *= 1 - q
            if w.loop == "trail":
                for k in range(3, 0, -1):
                    blit(frame, spr, w.x + dx - 70 * k, w.y + dy, s, rot, a * 0.22 / k)
            blit(frame, spr, w.x + dx, w.y + dy, s, rot, a)


def build_captions():
    B = []
    # A: namanya juga lagi MUSIM HUJAN der
    B.append(Block([
        [Word("NAMANYA", 1.18), Word("JUGA", 1.68), Word("LAGI", 1.86)],
        [Word("MUSIM", 2.04, "anton", 150, (WHITE, CYAN), "drop", hl=False, glow="#0090FF"),
         Word("HUJAN", 2.34, "anton", 150, (WHITE, CYAN), "drop", hl=False, glow="#0090FF")],
    ], cy=1420, t_end=3.02))
    # B: jadi JANGAN HERAN
    B.append(Block([
        [Word("JADI", 3.34, size=74)],
        [Word("JANGAN", 3.54, "anton", 140, (YELLOW, "#FF9F1C"), "stamp", hl=False),
         Word("HERAN", 3.80, "anton", 140, (YELLOW, "#FF9F1C"), "stamp", hl=False, loop="shake")],
    ], cy=1430, t_end=4.40))
    # C1: kalau banyak yang KEPLESET
    B.append(Block([
        [Word("KALAU", 4.56, size=74), Word("BANYAK", 4.76, size=74), Word("YANG", 5.12, size=74)],
        [Word("KEPLESET", 5.36, "bangers", 175, ("#FF7AA2", PINK), "slip", hl=False, glow="#FF0055")],
    ], cy=1430, t_end=5.76, out_dur=0.1))
    # C2: karena OMONGAN SENDIRI
    B.append(Block([
        [Word("KARENA", 5.86, size=74)],
        [Word("OMONGAN", 6.12, "anton", 135, (YELLOW, "#FFB703"), "stamp", hl=False),
         Word("SENDIRI", 6.52, "anton", 135, (YELLOW, "#FFB703"), "stamp", hl=False)],
    ], cy=1430, t_end=6.96))
    # E: ENJOY IN AJA
    B.append(Block([
        [Word("ENJOY", 8.33, "anton", 150, (YELLOW, "#FF7B00"), "pop", hl=False, loop="float"),
         Word("IN", 8.62, "anton", 150, WHITE, "pop", hl=False, loop="float"),
         Word("AJA", 8.85, "anton", 150, WHITE, "pop", hl=False, loop="float")],
    ], cy=1430, t_end=9.55))
    # G: ADUDU LARI-LARI
    B.append(Block([
        [Word("ADUDU", 10.93, "bangers", 150, (YELLOW, "#FF9F1C"), "pop", hl=False, loop="wobble")],
        [Word("LARI-LARI", 11.46, "anton", 140, WHITE, "slide", hl=False, loop="trail")],
    ], cy=1400, t_end=12.22))
    # H: aduh ada yang NELEN LUDAH SENDIRI
    B.append(Block([
        [Word("ADUH", 12.50, size=74), Word("ADA", 12.80, size=74), Word("YANG", 13.06, size=74)],
        [Word("NELEN", 13.28, "anton", 140, (WHITE, CYAN), "stamp", hl=False, glow="#0090FF"),
         Word("LUDAH", 13.46, "anton", 140, (WHITE, CYAN), "stamp", hl=False, glow="#0090FF")],
        [Word("SENDIRI", 13.88, "anton", 140, (YELLOW, "#FFB703"), "stamp", hl=False)],
    ], cy=1330, t_end=14.42))
    return B


# ======================================================================= assets
class Assets:
    def __init__(self):
        self.captions = build_captions()
        self.title_musim = text_sprite("MUSIM", "anton", 270, WHITE, stroke=12, glow="#00A2FF")
        self.title_hujan = text_sprite("HUJAN", "anton", 270, (CYAN, "#1E7BFF"), stroke=12, glow="#00A2FF")
        self.title_sub = text_sprite("EDISI: KEPLESET OMONGAN SENDIRI", "black", 44, YELLOW, stroke=6)
        self.badge = badge_sprite("MUSIM HUJAN", "🌧", 72)
        self.rec = text_sprite("REC", "mono", 40, WHITE, stroke=4, shadow=0.5)
        self.digits = {c: text_sprite(c, "mono", 34, WHITE, stroke=4, shadow=0.5) for c in "0123456789:"}
        self.der = text_sprite("DER!", "bangers", 110, YELLOW, stroke=10)
        self.wk = [text_sprite(c, "bangers", 165, WHITE if i % 2 else YELLOW, stroke=12)
                   for i, c in enumerate("WKWKWK")]
        self.kabur = text_sprite("KABUURR!!", "bangers", 170, ("#FFE066", "#FF3D3D"), stroke=13,
                                 glow="#FF2200")
        self.glek = text_sprite("GLEK!", "bangers", 120, "#111111", stroke=0, shadow=0)
        self.burst = comic_burst_sprite(175)
        self.sign = warning_sign_sprite(290)
        self.tape = hazard_tape_sprite(2700, 92)
        self.star = starburst_sprite(400)
        self.end_hati = text_sprite("HATI-HATI", "black", 92, WHITE, stroke=9)
        self.end_kep = text_sprite("KEPLESET", "bangers", 220, ("#FF7AA2", PINK), stroke=16, glow="#FF0055")
        self.end_omg = text_sprite("OMONGAN SENDIRI", "anton", 128, (YELLOW, "#FFB703"), stroke=11)
        e = emoji_sprite
        self.emo = {
            "rain": e("🌧", 190), "shrug": e("🤷", 150), "banana": e("🍌", 150),
            "speak": e("🗣", 140), "joy": e("😂", 130), "cool": e("😎", 150),
            "shaka": e("🤙", 150), "run": e("🏃", 190, flip=True), "dash": e("💨", 130, flip=True),
            "oops": e("🤭", 160), "drop": e("💦", 120), "bolt": e("⚡", 150), "spark": e("✨", 90),
        }
        self.joy_small = e("😂", 95)
        self.rain = fx.Rain(W, H)
        self.vig = fx.vignette(W, H, 0.6)
        self.grain = fx.grain_bank(W, H, amount=0.022)
        self.lower = fx.vertical_gradient(W, H, 1080, 1760, 1420, 0.42)
        self.bolt_core, self.bolt_glow = fx.lightning_layer(W, H, seed=5)


A = None
FRAMES = None
LAST_FRAME = None


# ======================================================================= source stage
def remove_subs(img, idx):
    if not any(a - 1 <= idx <= b + 1 for a, b in SUB_FRAMES):
        return img
    band = img[748:852].astype(np.int16)
    core = (band.min(axis=2) > 228) & ((band.max(axis=2) - band.min(axis=2)) < 20)
    mask = cv2.dilate(core.astype(np.uint8) * 255,
                      cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    filled = cv2.inpaint(np.ascontiguousarray(img[748:852]), mask, 6, cv2.INPAINT_TELEA)
    # soften the patched area so leftover outline specks disappear
    soft = cv2.GaussianBlur(cv2.dilate(mask, np.ones((5, 5), np.uint8)), (0, 0), 3)[..., None] / 255.0
    filled = filled * (1 - soft) + cv2.GaussianBlur(filled, (0, 0), 2.5) * soft
    out = img.copy()
    out[748:852] = filled.astype(np.uint8)
    return out


def camera(t):
    """Returns (zoom, rotation_deg, tx, ty) for the virtual camera."""
    z, rot, tx, ty = 1.05, 0.0, 0.0, 0.0
    if t < 1.2:
        z += 0.22 * (1 - ease_out_cubic(t / 1.2))
    for t0, amt in [(1.15, 0.07), (2.04, 0.04), (2.34, 0.08), (3.54, 0.04), (3.80, 0.07),
                    (5.36, 0.10), (6.12, 0.08), (6.52, 0.06), (8.33, 0.06), (10.93, 0.06),
                    (13.28, 0.08), (13.46, 0.05), (13.88, 0.07)]:
        z += amt * punch(t, t0, 0.05, 0.28)
    if 6.9 < t < SRC_END:
        z += sum(0.025 * punch(t, b, 0.03, 0.14) for b in BEATS)
    for a, b, amp in [(2.34, 2.9, 14), (3.80, 4.4, 8), (5.36, 5.9, 20), (6.12, 6.5, 10),
                      (9.75, 12.2, 9), (13.28, 14.3, 7)]:
        k = amp * window(t, a, b, 0.03, 0.25)
        tx += k * wobble(t * 2.2, a)
        ty += k * wobble(t * 2.5, a + 3)
        rot += k * 0.05 * wobble(t * 1.7, a + 7)
    u = t - 5.36
    if u > 0:
        k = spring(u, 1.8, 3.5)
        rot -= 6 * k
        tx -= 70 * k
    if t > SRC_END:  # end card: slow push in on the frozen frame
        z += 0.06 * ease_out_cubic((t - SRC_END) / END_CARD)
    rot_r = math.radians(abs(rot))
    z += 0.7 * (math.cos(rot_r) + (H / W) * math.sin(rot_r) - 1)
    return z, rot, tx, ty


def base_frame(idx, t):
    if t <= SRC_END and idx < len(FRAMES):
        img = remove_subs(FRAMES[idx], idx)
        blur = 7 * (1 - ease_out_cubic(t / 1.1)) if t < 1.1 else 0
        bright = 0.55 + 0.45 * ease_out_cubic(t / 1.1) if t < 1.1 else 1.0
    else:
        img = remove_subs(LAST_FRAME, SRC_FRAMES - 1)
        p = ease_out_cubic((t - SRC_END) / 0.4)
        blur, bright = 6 * p, 1 - 0.5 * p
    img = fx.grade(img, 1.1, bright)
    if blur > 0.3:
        img = cv2.GaussianBlur(img, (0, 0), blur)
    z, rot, tx, ty = camera(t)
    m = cv2.getRotationMatrix2D((SW / 2, SH / 2), rot, z * W / SW)
    m[0, 2] += W / 2 - SW / 2 + tx
    m[1, 2] += H / 2 - SH / 2 + ty
    out = cv2.warpAffine(img, m, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT101)
    if blur <= 0.3:
        soft = cv2.GaussianBlur(out, (0, 0), 1.4)
        out = cv2.addWeighted(out, 1.6, soft, -0.6, 0)
    return out.astype(np.float32) / 255.0


# ======================================================================= overlays
def draw_intro(f, t):
    if t > 1.3:
        return
    out = clamp((t - 0.95) / 0.2)
    s_out = 1 + 0.5 * ease_in_cubic(out)
    a_out = 1 - out
    p1 = ease_out_expo((t - 0.03) / 0.35)
    p2 = ease_out_expo((t - 0.15) / 0.35)
    if t >= 0.03:
        blit(f, A.title_musim, W / 2 - 900 * (1 - p1), 800 + (800 - 960) * (s_out - 1),
             s_out, 0, clamp((t - 0.03) / 0.08) * a_out)
    if t >= 0.15:
        blit(f, A.title_hujan, W / 2 + 900 * (1 - p2), 1050 + (1050 - 960) * (s_out - 1),
             s_out, 0, clamp((t - 0.15) / 0.08) * a_out)
    bar = ease_out_cubic((t - 0.3) / 0.25)
    if bar > 0 and a_out > 0:
        x0, x1 = int(W / 2 - 330 * bar * s_out), int(W / 2 + 330 * bar * s_out)
        f[921:933, x0:x1] = f[921:933, x0:x1] * (1 - a_out) + np.array([1, 0.84, 0.04]) * a_out
    if t >= 0.42:
        blit(f, A.title_sub, W / 2, 1235, 1, 0, a_out, reveal=clamp((t - 0.42) / 0.45))
    if t >= 0.3:
        blit(f, A.emo["rain"], 870, 610, back_out((t - 0.3) / 0.3) * s_out,
             8 * math.sin(t * 6), a_out)


def draw_hud(f, t):
    # progress bar
    p = clamp(t / TOTAL)
    xs = int(W * p)
    if xs > 0:
        grad = np.linspace(0, 1, xs, dtype=np.float32)[:, None]
        col = np.array([0.18, 0.9, 1.0]) * (1 - grad) + np.array([1.0, 0.84, 0.04]) * grad
        f[0:10, :xs] = col[None, :, :]
    if t < 1.15 or t > SRC_END + 0.05:
        return
    u = t - 1.15
    blit(f, A.badge, 70 + A.badge.w / 2 - 40, 225, back_out(u / 0.35), 0, clamp(u / 0.1))
    # REC dot + timecode
    a = clamp(u / 0.2)
    if int(t * 2) % 2 == 0:
        cv2.circle(f, (842, 226), 13, (1.0, 0.15, 0.2), -1, cv2.LINE_AA)
    blit(f, A.rec, 902, 226, 1, 0, a)
    secs = int(t)
    frames = int((t - secs) * FPS)
    tc = f"00:{secs:02d}:{frames:02d}"
    x = 1030 - 21 * len(tc)
    for ch in tc:
        blit(f, A.digits[ch], x, 282, 1, 0, a * 0.85)
        x += 21
    # viewfinder corners
    col = np.array([1, 1, 1], np.float32)
    for (cx, cy, sx, sy) in [(46, 330, 1, 1), (1034, 330, -1, 1), (46, 1590, 1, -1), (1034, 1590, -1, -1)]:
        x0, x1 = sorted((cx, cx + 70 * sx))
        y0, y1 = sorted((cy, cy + 70 * sy))
        f[cy - 2:cy + 3, x0:x1] = f[cy - 2:cy + 3, x0:x1] * 0.4 + col * 0.6 * a
        f[y0:y1, cx - 2:cx + 3] = f[y0:y1, cx - 2:cx + 3] * 0.4 + col * 0.6 * a


def draw_sections(f, t):
    e = A.emo
    # A — "DER!" sticker + lightning emoji
    if 2.72 <= t <= 3.1:
        u = t - 2.72
        a = 1 - clamp((t - 2.98) / 0.12)
        blit(f, A.der, 900, 1215, back_out(u / 0.22), 12 + 5 * spring(u, 4, 6), a)
    if 2.34 <= t <= 3.08:
        u = t - 2.34
        blit(f, e["bolt"], 135, 1225, back_out(u / 0.25), -12, 1 - clamp((t - 2.95) / 0.12))
    # B — shrug
    if 3.80 <= t <= 4.55:
        u = t - 3.80
        blit(f, e["shrug"], 915, 1280, back_out(u / 0.3), 10 + 4 * math.sin(u * 9),
             1 - clamp((t - 4.42) / 0.12))
    # C — hazard tape, warning sign, banana, speaking head
    if 5.30 <= t <= 7.25:
        u = t - 5.30
        out = ease_in_cubic((t - 6.95) / 0.3)
        for i, (y, ang, dirn) in enumerate([(430, -7, 1), (575, 5, -1)]):
            slide = (1 - ease_out_expo((u - 0.08 * i) / 0.35)) * 1600 * dirn
            scroll = ((t * 260 * dirn) % 380) - 190
            blit(f, A.tape, W / 2 + slide + scroll + out * 1600 * dirn, y, 1, ang, 1 - 0.2 * out)
    if 5.40 <= t <= 7.0:
        u = t - 5.40
        blit(f, A.sign, 225, 820, back_out(u / 0.35), 14 * spring(u, 2.2, 3) + 4 * math.sin(u * 5),
             1 - clamp((t - 6.85) / 0.15))
    if 5.36 <= t <= 5.86:
        u = t - 5.36
        blit(f, e["banana"], 150 + 900 * ease_out_cubic(u / 0.5), 1600, 1, -u * 900,
             1 - clamp((t - 5.75) / 0.11))
    if 6.12 <= t <= 7.0:
        u = t - 6.12
        blit(f, e["speak"], 150, 1300, back_out(u / 0.3), -8, 1 - clamp((t - 6.88) / 0.12))
    # D — WKWKWK wave + rising laughing emojis
    if 6.98 <= t <= 8.35:
        u = t - 6.98
        a = 1 - clamp((t - 8.2) / 0.15)
        x = W / 2 - 5 * 105 / 2 - 52
        for i, spr in enumerate(A.wk):
            ui = u - 0.06 * i
            if ui < 0:
                continue
            y = 560 - 40 * abs(math.sin(2 * math.pi * 1.6 * ui))
            blit(f, spr, x + i * 115, y, back_out(ui / 0.25), 8 * math.sin(ui * 8 + i), a)
        rng = np.random.default_rng(4)
        for k in range(9):
            st = 0.05 + k * 0.14
            uk = u - st
            if uk < 0:
                continue
            x0 = rng.uniform(80, W - 80)
            y = 1850 - 900 * uk
            blit(f, A.joy_small if k % 2 else e["joy"], x0 + 40 * math.sin(uk * 5 + k), y,
                 1, 20 * math.sin(uk * 4 + k), a * clamp(uk / 0.1))
    # E — starburst + sparkles + emojis (drawn under the caption)
    if 8.30 <= t <= 9.65:
        u = t - 8.30
        a = clamp(u / 0.2) * (1 - clamp((t - 9.45) / 0.2))
        blit(f, A.star, W / 2, 1440, 0.6 + 0.4 * ease_out_cubic(u / 0.4), u * 40, 0.2 * a)
        blit(f, e["cool"], 165, 1250, back_out((u - 0.05) / 0.3) if u > 0.05 else 0, -10, a)
        blit(f, e["shaka"], 915, 1260, back_out((u - 0.5) / 0.3) if u > 0.5 else 0,
             12 + 10 * math.sin(u * 10), a)
        for k, (sx, sy) in enumerate([(250, 1560), (840, 1580), (520, 1255), (980, 1450), (90, 1450)]):
            tw = 0.5 + 0.5 * math.sin(u * 9 + k * 1.7)
            blit(f, e["spark"], sx, sy, 0.6 + 0.5 * tw, k * 20, a * tw)


def draw_late_sections(f, t):
    e = A.emo
    # F — KABUURR!!
    if 9.70 <= t <= 10.95:
        u = t - 9.70
        a = 1 - clamp((t - 10.8) / 0.15)
        x = W / 2 + 6 * wobble(t * 4, 1)
        y = 720 + 6 * wobble(t * 4.4, 2)
        for k in range(3, 0, -1):
            blit(f, A.kabur, x - 60 * k, y, back_out(u / 0.25), -8, a * 0.2 / k)
        blit(f, A.kabur, x, y, back_out(u / 0.25), -8, a)
        blit(f, e["dash"], 120, 860, back_out((u - 0.15) / 0.3) if u > 0.15 else 0, 0, a)
    # G — running emoji across the screen
    if 10.95 <= t <= 12.25:
        u = t - 10.95
        x = -150 + (W + 300) * (u / 1.3)
        bob = abs(math.sin(u * 14)) * 25
        blit(f, e["dash"], x - 150, 880 - bob * 0.3, 0.8, 0, 0.8)
        blit(f, e["run"], x, 860 - bob, 1, 6 * math.sin(u * 14), 1)
    # H — GLEK! burst + emojis
    if 13.46 <= t <= 14.45:
        u = t - 13.46
        a = 1 - clamp((t - 14.3) / 0.15)
        s = back_out(u / 0.25)
        rot = -10 + 6 * spring(u, 3, 5)
        blit(f, A.burst, 805, 560, s, rot + u * 20, a)
        blit(f, A.glek, 805, 560, s, rot, a)
        blit(f, e["drop"], 640, 450, back_out((u - 0.1) / 0.3) if u > 0.1 else 0, -20, a)
    if 13.88 <= t <= 14.45:
        u = t - 13.88
        blit(f, e["oops"], 900, 1500, back_out(u / 0.3), 10 * math.sin(u * 8),
             1 - clamp((t - 14.3) / 0.15))


def draw_end_card(f, t):
    u = t - SRC_END
    if u < 0:
        return
    a = 1 - clamp((t - (TOTAL - 0.3)) / 0.3)
    blit(f, A.badge, W / 2, 560, back_out((u - 0.05) / 0.3) * 1.3 if u > 0.05 else 0, 0, a)
    if u > 0.12:
        uu = u - 0.12
        blit(f, A.end_hati, W / 2, 760, 0.3 + 0.7 * back_out(uu / 0.25), 0, a * clamp(uu / 0.08))
    if u > 0.32:
        uu = u - 0.32
        k = spring(uu - 0.2, 2.6, 4.2) if uu > 0.2 else 0
        blit(f, A.end_kep, W / 2 - 700 * (1 - ease_out_expo(uu / 0.22)) + 40 * k, 950,
             1, -12 * k, a * clamp(uu / 0.06))
    if u > 0.62:
        uu = u - 0.62
        s = 1 + 1.6 * (1 - ease_out_cubic(uu / 0.15))
        blit(f, A.end_omg, W / 2, 1135, s, 0, a * clamp(uu / 0.05))
    if u > 0.85:
        uu = u - 0.85
        blit(f, A.emo["oops"], 880, 1290, back_out(uu / 0.3), 10 * math.sin(uu * 7), a)
        blit(f, A.emo["joy"], 200, 1290, back_out((uu - 0.1) / 0.3) if uu > 0.1 else 0,
             -10 * math.sin(uu * 7), a)


# ======================================================================= frame
FLASHES = [(1.15, (1, 1, 1), 0.85, 0.16), (5.36, (1, 1, 1), 0.45, 0.12), (6.12, (1, 0.95, 0.7), 0.35, 0.12),
           (8.33, (1, 0.8, 0.5), 0.35, 0.18), (10.93, (1, 1, 1), 0.4, 0.12), (13.28, (0.7, 0.95, 1), 0.45, 0.14),
           (SRC_END, (1, 1, 1), 1.0, 0.22)]
GLITCHES = [(0.0, 0.16), (1.08, 1.2), (6.92, 7.04), (9.28, 9.42), (12.16, 12.46), (13.28, 13.36),
            (14.58, SRC_END + 0.05), (TOTAL - 0.35, TOTAL - 0.25)]


def render_frame(idx):
    t = idx / FPS
    f = base_frame(idx, t)

    # whip pans: camera swing to the road and up to the sky
    whip = 60 * window(t, 9.28, 9.62, 0.08, 0.2) + 40 * window(t, 14.6, SRC_END + 0.08, 0.06, 0.06)
    if whip > 2:
        f = fx.motion_blur(f, whip)
    vwhip = 50 * window(t, 12.15, 12.48, 0.08, 0.15)
    if vwhip > 2:
        f = fx.motion_blur(f, vwhip, vertical=True)

    fx.bloom(f, 0.35 + 0.55 * window(t, 12.2, TOTAL, 0.4, 0.01))

    # lightning on "HUJAN"
    u = t - 2.34
    if 0 <= u < 0.5:
        flick = [1, 0.2, 0.9, 0.1, 0.6, 0.35, 0.15, 0.05][min(7, int(u * FPS / 2))]
        f += (A.bolt_glow[..., None] * np.array([0.55, 0.75, 1.0]) + A.bolt_core[..., None]) * flick
        fx.flash(f, (0.8, 0.9, 1.0), 0.55 * flick)

    rain_amt = 0.55 + 0.45 * window(t, 2.34, 4.6, 0.05, 0.8) + 0.3 * window(t, SRC_END, TOTAL, 0.3, 0.3)
    fx.apply_rain(f, A.rain.render(t, rain_amt), 0.8)

    leak = fx.light_leak(W, H, t, 0.12 * window(t, 0, 1.4, 0.01, 0.3) + 0.12 * window(t, 8.2, 9.8, 0.2, 0.4)
                         + 0.1 * window(t, SRC_END, TOTAL, 0.2, 0.3))
    if leak is not None:
        f += leak

    spd = window(t, 9.72, 12.22, 0.1, 0.15)
    if spd > 0:
        lines = fx.speed_lines(W, H, W / 2, 900, idx, 0.55 * spd)
        f += lines[..., None]

    if t < SRC_END:
        f *= 1 - A.lower * window(t, 1.1, 14.45, 0.2, 0.2)

    draw_intro(f, t)
    for block in A.captions:
        block.draw(f, t)
    draw_sections(f, t)
    draw_late_sections(f, t)
    draw_end_card(f, t)
    draw_hud(f, t)

    for t0, col, amt, dec in FLASHES:
        fx.flash(f, col, amt * punch(t, t0, 0.01, dec))
    for a, b in GLITCHES:
        g = window(t, a, b, 0.02, 0.02)
        if g > 0:
            fx.glitch(f, g, idx * 31 + 7)
    beat = sum(punch(t, b, 0.02, 0.1) for b in BEATS) if 6.9 < t < SRC_END else 0
    if beat > 0.05:
        fx.chroma_split(f, 5 * beat)

    f *= A.vig
    f += A.grain[idx % len(A.grain)]
    if t > TOTAL - 0.3:
        f *= 1 - ease_in_cubic((t - (TOTAL - 0.3)) / 0.3)
    return (np.clip(f, 0, 1) * 255).astype(np.uint8)


# ======================================================================= io
def load_frames():
    proc = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC), "-f", "rawvideo",
                           "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    frames = np.frombuffer(proc.stdout, np.uint8).reshape(-1, SH, SW, 3)
    return frames


def build_audio(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC), "-f", "s16le", "-ac", "2",
                          "-ar", str(sfx.SR), "-"], capture_output=True, check=True).stdout
    src = np.frombuffer(pcm, np.int16).reshape(-1, 2).astype(np.float64) / 32768
    E = [
        (0.0, "glitch", 0.35, 0), (0.02, "whoosh", 0.55, -0.5), (0.14, "whoosh", 0.5, 0.5),
        (0.3, "pop", 0.4, 0.4), (0.65, "riser", 0.4, 0), (1.15, "impact", 0.7, 0),
        (2.04, "pop", 0.3, 0), (2.34, "thunder", 0.75, 0.1), (2.72, "pop", 0.3, 0.4),
        (3.54, "pop", 0.3, 0), (3.80, "impact", 0.35, 0), (5.36, "slip", 0.32, 0),
        (5.30, "whoosh", 0.4, -0.4), (5.40, "pop", 0.3, -0.5), (6.12, "impact", 0.5, 0),
        (6.52, "impact", 0.4, 0), (6.92, "glitch", 0.3, 0), (8.30, "sparkle", 0.35, 0),
        (9.28, "whoosh", 0.65, 0.3), (9.70, "pop", 0.35, 0), (10.93, "pop", 0.35, 0),
        (11.0, "whoosh", 0.45, -0.6), (11.46, "whoosh", 0.4, 0.4), (12.16, "glitch", 0.35, 0),
        (13.28, "impact", 0.5, 0), (13.46, "gulp", 0.6, 0.3), (13.88, "pop", 0.35, 0.4),
        (14.25, "riser", 0.45, 0), (SRC_END, "impact", 0.85, 0), (SRC_END + 0.12, "pop", 0.35, 0),
        (SRC_END + 0.32, "slip", 0.3, 0), (SRC_END + 0.62, "impact", 0.55, 0),
        (SRC_END + 0.85, "pop", 0.3, 0.4), (TOTAL - 0.45, "whoosh", 0.4, 0),
    ]
    out = sfx.mix(src, E, TOTAL, end_card=True)
    pcm16 = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sfx.SR)
        w.writeframes(pcm16.tobytes())


def render_video():
    global A, FRAMES, LAST_FRAME
    A = Assets()
    FRAMES = load_frames()
    LAST_FRAME = FRAMES[-1]
    assert len(FRAMES) >= SRC_FRAMES - 2, len(FRAMES)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wav = OUT.with_suffix(".wav")
    build_audio(wav)
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-i", str(wav),
        "-af", "alimiter=limit=0.95:level=disabled",
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "12M", "-bufsize", "24M",
        "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        "-shortest", str(OUT)], stdin=subprocess.PIPE)
    with get_context("fork").Pool(4) as pool:
        for i, frame in enumerate(pool.imap(render_frame, range(N_FRAMES), chunksize=4)):
            enc.stdin.write(frame.tobytes())
            if i % 30 == 0:
                print(f"frame {i}/{N_FRAMES}", file=sys.stderr, flush=True)
    enc.stdin.close()
    enc.wait()
    wav.unlink()
    print(f"done -> {OUT}")


def preview(times):
    global A, FRAMES, LAST_FRAME
    A = Assets()
    FRAMES = load_frames()
    LAST_FRAME = FRAMES[-1]
    out_dir = ROOT / "output" / "preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    for t in times:
        idx = int(round(t * FPS))
        img = render_frame(idx)
        path = out_dir / f"t{t:05.2f}.jpg"
        cv2.imwrite(str(path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        print(path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", nargs="+", type=float, help="render single frames at these times")
    args = ap.parse_args()
    if args.preview:
        preview(args.preview)
    else:
        render_video()
