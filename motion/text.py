"""Sprites (text, emoji stickers, shapes) and a fast premultiplied-alpha compositor."""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
FONTS = {
    "black": (FONT_DIR / "Montserrat-VF.ttf", "Black"),
    "anton": (FONT_DIR / "Anton-Regular.ttf", None),
    "bangers": (FONT_DIR / "Bangers-Regular.ttf", None),
    "mono": (FONT_DIR / "JetBrainsMono-ExtraBold.ttf", None),
}

_fonts = {}


def get_font(name, size):
    key = (name, size)
    if key not in _fonts:
        path, variation = FONTS[name]
        font = ImageFont.truetype(str(path), size)
        if variation:
            font.set_variation_by_name(variation)
        _fonts[key] = font
    return _fonts[key]


def rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


class Sprite:
    """Premultiplied RGBA float32 image. Its centre is the anchor point."""

    def __init__(self, data, ink_w=None, ink_h=None):
        self.data = np.ascontiguousarray(data, np.float32)
        self.h, self.w = data.shape[:2]
        self.ink_w = ink_w or self.w
        self.ink_h = ink_h or self.h


def to_sprite(img, ink_w=None, ink_h=None):
    arr = np.asarray(img.convert("RGBA"), np.float32) / 255.0
    arr[..., :3] *= arr[..., 3:4]
    return Sprite(arr, ink_w, ink_h)


def _paint(fill, size, top, height):
    """Solid colour, or a vertical gradient (top, bottom) spanning the ink box."""
    w, h = size
    if isinstance(fill, str):
        return Image.new("RGB", size, rgb(fill))
    c1, c2 = (np.array(rgb(c), np.float32) for c in fill)
    t = np.clip((np.arange(h, dtype=np.float32) - top) / max(height, 1), 0, 1)[:, None]
    col = c1 * (1 - t) + c2 * t
    arr = np.repeat(col[:, None, :], w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _layer(color, alpha):
    layer = Image.new("RGBA", alpha.size, rgb(color) + (0,))
    layer.putalpha(alpha)
    return layer


def text_sprite(text, font="black", size=80, fill="#FFFFFF", stroke=8,
                stroke_fill="#000000", shadow=0.65, glow=None, skew=0.0):
    f = get_font(font, size)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    x0, y0, x1, y1 = probe.textbbox((0, 0), text, font=f, stroke_width=stroke)
    iw, ih = x1 - x0, y1 - y0
    blur = 16 if glow else 7
    pad = stroke + blur * 2 + 14 + int(abs(skew) * ih)
    size_wh = (iw + 2 * pad, ih + 2 * pad)
    org = (pad - x0, pad - y0)

    fill_mask = Image.new("L", size_wh)
    ImageDraw.Draw(fill_mask).text(org, text, font=f, fill=255)
    full_mask = Image.new("L", size_wh)
    ImageDraw.Draw(full_mask).text(org, text, font=f, fill=255,
                                   stroke_width=stroke, stroke_fill=255)

    out = Image.new("RGBA", size_wh, (0, 0, 0, 0))
    if glow:
        g = full_mask.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: min(255, int(v * 1.8)))
        out = Image.alpha_composite(out, _layer(glow, g))
    if shadow:
        s = full_mask.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * shadow))
        shifted = Image.new("L", size_wh)
        shifted.paste(s, (int(size * 0.03), int(size * 0.07)))
        out = Image.alpha_composite(out, _layer("#000000", shifted))
    if stroke:
        out = Image.alpha_composite(out, _layer(stroke_fill, full_mask))
    face = _paint(fill, size_wh, pad, ih).convert("RGBA")
    face.putalpha(fill_mask)
    out = Image.alpha_composite(out, face)
    if skew:
        w, h = size_wh
        out = out.transform(size_wh, Image.AFFINE, (1, skew, -skew * h / 2, 0, 1, 0),
                            resample=Image.BICUBIC)
    return to_sprite(out, iw, ih)


def _sticker(img, outline, shadow=True):
    """White die-cut border + soft shadow around an RGBA image."""
    pad = outline + 18
    w, h = img.width + 2 * pad, img.height + 2 * pad
    base = Image.new("RGBA", (w, h))
    base.paste(img, (pad, pad))
    alpha = np.asarray(base.getchannel("A"))
    out = Image.new("RGBA", (w, h))
    if outline:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (outline * 2 + 1, outline * 2 + 1))
        border = Image.fromarray(cv2.dilate(alpha, k))
        if shadow:
            s = border.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.55))
            shifted = Image.new("L", (w, h))
            shifted.paste(s, (4, 8))
            out = Image.alpha_composite(out, _layer("#000000", shifted))
        out = Image.alpha_composite(out, _layer("#FFFFFF", border))
    return Image.alpha_composite(out, base)


def emoji_image(char, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (200, 200))
    ImageDraw.Draw(im).text((20, 20), char, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    k = size / max(im.size)
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)


def emoji_sprite(char, size=120, outline=9, flip=False):
    im = emoji_image(char, size)
    if flip:
        im = ImageOps.mirror(im)
    return to_sprite(_sticker(im, outline))


def supersample(w, h, draw_fn, k=3):
    """Draw at k× resolution with PIL, then downsample for anti-aliased shapes."""
    big = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(big), k)
    return big.resize((w, h), Image.LANCZOS)


def badge_sprite(label, emoji, height=74, bg="#22D3EE", fg="#04121A"):
    f = get_font("black", int(height * 0.48))
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    x0, y0, x1, y1 = probe.textbbox((0, 0), label, font=f)
    em_img = emoji_image(emoji, int(height * 0.72))
    w = int(height * 0.35) + em_img.width + int(height * 0.2) + (x1 - x0) + int(height * 0.45)

    def draw(d, k):
        d.rounded_rectangle([0, 0, w * k - 1, height * k - 1], radius=height * k // 2, fill=rgb(bg))

    img = supersample(w, height, draw)
    img.alpha_composite(em_img, (int(height * 0.35), (height - em_img.height) // 2))
    ImageDraw.Draw(img).text((int(height * 0.35) + em_img.width + int(height * 0.2) - x0,
                              (height - (y1 - y0)) // 2 - y0), label, font=f, fill=rgb(fg))
    return to_sprite(_sticker(img, 0))


def warning_sign_sprite(size=300, label="LICIN!"):
    def draw(d, k):
        s = size * k
        c = s / 2
        r = s * 0.48
        d.regular_polygon((c, c, r), 4, rotation=45, fill=rgb("#111111"))
        d.regular_polygon((c, c, r * 0.86), 4, rotation=45, fill=rgb("#FFD60A"))
        d.regular_polygon((c, c, r * 0.76), 4, rotation=45, outline=rgb("#111111"), width=int(4 * k))

    img = supersample(size, size, draw)
    f = get_font("anton", int(size * 0.17))
    d = ImageDraw.Draw(img)
    for text, y in (("AWAS", 0.41), (label, 0.6)):
        x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
        d.text(((size - (x1 - x0)) / 2 - x0, size * y - (y1 - y0) / 2 - y0), text, font=f,
               fill=rgb("#111111"))
    return to_sprite(_sticker(img, 8))


def hazard_tape_sprite(length=2600, height=96, text="AWAS LICIN"):
    stripe = height // 5

    def draw(d, k):
        L, H, st = length * k, height * k, stripe * k
        d.rectangle([0, 0, L, H], fill=rgb("#FFD60A"))
        for band_top in (0, H - st):
            for x in range(-H, L + H, 2 * st):
                d.polygon([(x, band_top + st), (x + st, band_top), (x + 2 * st, band_top),
                           (x + st, band_top + st)], fill=rgb("#111111"))

    img = supersample(length, height, draw, k=2)
    f = get_font("anton", int(height * 0.5))
    d = ImageDraw.Draw(img)
    unit = f"{text}  •  "
    x0, y0, x1, y1 = d.textbbox((0, 0), unit, font=f)
    x = 10
    while x < length:
        d.text((x - x0, height / 2 - (y1 - y0) / 2 - y0), unit, font=f, fill=rgb("#111111"))
        x += x1 - x0
    alpha = Image.new("L", (length, height + 30))
    alpha.paste(Image.new("L", (length, height), 150), (0, 14))
    shadow = _layer("#000000", alpha.filter(ImageFilter.GaussianBlur(8)))
    shadow.alpha_composite(img, (0, 4))
    return to_sprite(shadow)


def starburst_sprite(radius=520, rays=18, color="#FFD60A"):
    def draw(d, k):
        c = radius * k
        for i in range(rays):
            a0 = 2 * np.pi * i / rays
            a1 = a0 + np.pi / rays
            d.polygon([(c, c), (c + c * np.cos(a0), c + c * np.sin(a0)),
                       (c + c * np.cos(a1), c + c * np.sin(a1))], fill=rgb(color) + (255,))

    img = supersample(radius * 2, radius * 2, draw, k=2)
    # fade the rays towards the outside
    yy, xx = np.mgrid[0:radius * 2, 0:radius * 2]
    r = np.hypot(xx - radius, yy - radius) / radius
    fade = np.clip(1.2 - r, 0, 1) ** 1.3
    alpha = (np.asarray(img.getchannel("A"), np.float32) * fade).astype(np.uint8)
    img.putalpha(Image.fromarray(alpha))
    return to_sprite(img)


def comic_burst_sprite(radius=190, points=14, fill="#FFD60A", outline="#111111", seed=3):
    rng = np.random.default_rng(seed)
    radii = np.where(np.arange(points * 2) % 2 == 0, 1.0, 0.62) * rng.uniform(0.88, 1.0, points * 2)

    def draw(d, k):
        c = radius * k
        pts = [(c + c * 0.97 * rr * np.cos(np.pi * i / points), c + c * 0.97 * rr * np.sin(np.pi * i / points))
               for i, rr in enumerate(radii)]
        d.polygon(pts, fill=rgb(outline))
        inner = [(c + (x - c) * 0.88, c + (y - c) * 0.88) for x, y in pts]
        d.polygon(inner, fill=rgb(fill))

    return to_sprite(_sticker(supersample(radius * 2, radius * 2, draw), 0))


def blit(dst, spr, cx, cy, scale=1.0, rot=0.0, alpha=1.0, reveal=1.0):
    """Composite a premultiplied sprite centred at (cx, cy) onto a float32 RGB frame.

    rot is in degrees (counter-clockwise). reveal < 1 crops the sprite from the right
    (typewriter wipe) and is only honoured for untransformed sprites.
    """
    if alpha <= 0.003 or scale <= 0.01:
        return
    data = spr.data
    h, w = data.shape[:2]
    if abs(scale - 1) > 1e-3 or abs(rot) > 0.05:
        m = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
        c, s = abs(m[0, 0]), abs(m[0, 1])
        nw, nh = int(w * c + h * s) + 2, int(w * s + h * c) + 2
        m[0, 2] += nw / 2 - w / 2
        m[1, 2] += nh / 2 - h / 2
        data = cv2.warpAffine(data, m, (nw, nh), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        h, w = nh, nw
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    if reveal < 1:
        pad = (spr.w - spr.ink_w) / 2
        data = data[:, :max(0, int(pad + spr.ink_w * reveal))]
        w = data.shape[1]
    H, W = dst.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(W, x0 + w), min(H, y0 + h)
    if dx1 <= dx0 or dy1 <= dy0:
        return
    src = data[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
    region = dst[dy0:dy1, dx0:dx1]
    a = src[..., 3:4] * alpha
    region *= 1 - a
    region += src[..., :3] * alpha
