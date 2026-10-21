"""Генерирует графику темы TempleOS 2026 в сыром формате для HolyC.

Форматы (little-endian):
  *.BGRA  — U32 width, U32 height, затем width*height пикселей U32 0xAARRGGBB
  FONT.BIN — U32 height, U32 ascent, 95 x U8 advance, затем для каждого глифа advance*height байт альфы
"""
import struct
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
OUT = Path(__file__).resolve().parent.parent / "theme" / "Theme" / "Assets"
OUT.mkdir(parents=True, exist_ok=True)
FONTS = Path("C:/Windows/Fonts")


def save_bgra(path, img):
    a = np.asarray(img.convert("RGBA"), dtype=np.uint32)
    px = (a[..., 3] << 24) | (a[..., 0] << 16) | (a[..., 1] << 8) | a[..., 2]
    with open(path, "wb") as f:
        f.write(struct.pack("<II", img.width, img.height))
        f.write(px.astype("<u4").tobytes())


def wallpaper():
    y, x = np.mgrid[0:H, 0:W].astype(np.float64)
    u, v = x / W, y / H
    img = np.zeros((H, W, 3))
    img[:] = np.array([9, 11, 22], float)
    # мягкие «северные» пятна: (центр x, центр y, радиус x, радиус y, цвет, сила)
    blobs = [
        (0.18, 0.22, 0.42, 0.38, (124, 58, 237), 0.85),
        (0.78, 0.18, 0.40, 0.30, (37, 99, 235), 0.80),
        (0.62, 0.78, 0.50, 0.36, (20, 184, 166), 0.55),
        (0.10, 0.92, 0.38, 0.30, (219, 39, 119), 0.45),
        (0.92, 0.70, 0.30, 0.30, (99, 102, 241), 0.50),
    ]
    for cx, cy, rx, ry, col, k in blobs:
        d = ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2
        g = np.exp(-d * 1.6) * k
        img += g[..., None] * (np.array(col, float) - img) * 0.9
    # световая лента по диагонали
    band = np.exp(-((v - 0.55 + (u - 0.5) * 0.55) / 0.07) ** 2) * 0.18
    img += band[..., None] * np.array([180, 200, 255])
    # виньетка
    vig = 1 - 0.45 * (((u - 0.5) * 1.3) ** 2 + ((v - 0.5) * 1.5) ** 2)
    img *= np.clip(vig, 0.35, 1)[..., None]
    # шум против полос градиента
    img += np.random.default_rng(7).normal(0, 1.4, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def glass(wall):
    g = wall.filter(ImageFilter.GaussianBlur(28))
    a = np.asarray(g, float)
    a = a * 0.52 + np.array([14, 16, 30]) * 0.48 + 6
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def rounded_grad(size, r, c1, c2):
    s = size * 4
    grad = Image.new("RGB", (s, s))
    d = ImageDraw.Draw(grad)
    for i in range(s):
        t = i / (s - 1)
        d.line([(0, i), (s, i)], fill=tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3)))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], r * 4, fill=255)
    img = grad.convert("RGBA")
    img.putalpha(mask)
    return img


def icon(kind):
    S = 48 * 4
    styles = {
        "TERM": ((52, 58, 84), (22, 25, 40)),
        "FILES": ((96, 165, 250), (37, 99, 235)),
        "EDIT": ((251, 191, 36), (234, 88, 12)),
        "GAMES": ((52, 211, 153), (5, 150, 105)),
        "PAINT": ((244, 114, 182), (147, 51, 234)),
        "ORACLE": ((253, 230, 138), (217, 119, 6)),
        "HELP": ((167, 139, 250), (79, 70, 229)),
    }
    img = rounded_grad(48, 12, *styles[kind])
    d = ImageDraw.Draw(img)
    white = (255, 255, 255, 255)
    f = lambda sz, bold=True: ImageFont.truetype(str(FONTS / ("segoeuib.ttf" if bold else "segoeui.ttf")), sz)
    if kind == "TERM":
        d.line([(50, 70), (90, 100), (50, 130)], fill=(125, 207, 255, 255), width=14, joint="curve")
        d.line([(102, 132), (146, 132)], fill=white, width=14)
    elif kind == "FILES":
        d.rounded_rectangle([34, 62, 158, 146], 14, fill=(255, 255, 255, 235))
        d.rounded_rectangle([34, 50, 96, 76], 10, fill=(255, 255, 255, 235))
        d.rounded_rectangle([34, 78, 158, 146], 14, fill=(191, 219, 254, 255))
    elif kind == "EDIT":
        d.rounded_rectangle([50, 34, 142, 158], 12, fill=white)
        for i, yy in enumerate(range(62, 140, 20)):
            d.line([(68, yy), (124 - (i == 3) * 26, yy)], fill=(234, 88, 12, 255), width=9)
    elif kind == "GAMES":
        d.rounded_rectangle([28, 66, 164, 134], 34, fill=white)
        d.line([(62, 100), (90, 100)], fill=(5, 150, 105, 255), width=10)
        d.line([(76, 86), (76, 114)], fill=(5, 150, 105, 255), width=10)
        d.ellipse([116, 84, 132, 100], fill=(5, 150, 105, 255))
        d.ellipse([132, 100, 148, 116], fill=(5, 150, 105, 255))
    elif kind == "PAINT":
        for (cx, cy, col) in [(76, 78, (253, 224, 71)), (116, 78, (125, 211, 252)), (96, 116, (255, 255, 255))]:
            d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=col + (235,))
    elif kind == "ORACLE":
        d.rectangle([88, 36, 104, 156], fill=white)
        d.rectangle([56, 68, 136, 84], fill=white)
    elif kind == "HELP":
        d.text((96, 98), "?", font=f(120), fill=white, anchor="mm")
    # блик сверху
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(hl).rounded_rectangle([4, 4, S - 5, S // 2], 40, fill=(255, 255, 255, 22))
    img = Image.alpha_composite(img, hl)
    return img.resize((48, 48), Image.LANCZOS)


def font_atlas(path, size, ttf):
    font = ImageFont.truetype(str(FONTS / ttf), size)
    asc, desc = font.getmetrics()
    h = asc + desc
    advs, glyphs = [], []
    for c in range(32, 127):
        ch = chr(c)
        adv = max(1, int(round(font.getlength(ch))))
        im = Image.new("L", (adv, h), 0)
        ImageDraw.Draw(im).text((0, 0), ch, font=font, fill=255)
        advs.append(adv)
        glyphs.append(im.tobytes())
    with open(path, "wb") as f:
        f.write(struct.pack("<II", h, asc))
        f.write(bytes(advs))
        for g in glyphs:
            f.write(g)


def logo():
    # фирменный значок: золотой крест в круге с градиентом
    S = 22 * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, S - 1, S - 1], fill=(250, 204, 21, 255))
    d.rectangle([S // 2 - 6, 14, S // 2 + 6, S - 14], fill=(30, 27, 75, 255))
    d.rectangle([22, S // 2 - 14, S - 22, S // 2 - 2], fill=(30, 27, 75, 255))
    return img.resize((22, 22), Image.LANCZOS)


if __name__ == "__main__":
    wall = wallpaper()
    wall.save(OUT.parents[2] / "wallpaper_preview.png")
    save_bgra(OUT / "WALL.BGRA", wall)
    save_bgra(OUT / "GLASS.BGRA", glass(wall))
    for k in ["TERM", "FILES", "EDIT", "GAMES", "PAINT", "ORACLE", "HELP"]:
        save_bgra(OUT / f"I{k}.BGRA", icon(k))
    save_bgra(OUT / "LOGO.BGRA", logo())
    font_atlas(OUT / "FONT.BIN", 15, "segoeuisb.ttf" if (FONTS / "segoeuisb.ttf").exists() else "segoeui.ttf")
    font_atlas(OUT / "FONTB.BIN", 15, "segoeuib.ttf")
    print("ok", sorted(p.name for p in OUT.iterdir()))
