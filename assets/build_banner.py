"""Banner for the Harigovind777 profile README.

Original artwork, generated. Anime dusk scene: the sun seen through a gyroid
scaffold -- the actual level-set geometry from the bone-scaffold work -- with a
lone figure on the ridge. Rendered at 4x and downsampled.

    python3 build_banner.py
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 4
W, H = 1600, 440
SW, SH = W * SS, H * SS
S = lambda v: int(round(v * SS))

random.seed(7)
np.random.seed(7)

HIRA_MIN = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
HIRA_GO = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"
MENLO = "/System/Library/Fonts/Menlo.ttc"

BONE = (243, 239, 231)
AMBER = (248, 194, 116)
CYAN = (152, 234, 238)
MUTED = (206, 178, 186)

HORIZON = 0.82
SUN = (0.615, 0.556, 120)  # cx, cy (fractions), radius in final px

EYEBROW = "B.TECH AI & ML  ’27  ·  CHINMAYA VISHWA VIDYAPEETH  ·  TRIVANDRUM"
NAME = "HARIGOVIND R"
TAGLINE = "Physics-informed ML for bone tissue engineering"
SUB = "voxel FEM  ·  co-kriging  ·  leakage-honest validation"


def font(path, px, index=0):
    try:
        return ImageFont.truetype(path, px, index=index)
    except Exception:
        return ImageFont.truetype(path, px)


def track(d, xy, text, f, fill, tr=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tr


def twid(d, text, f, tr=0):
    return sum(d.textlength(c, font=f) + tr for c in text) - tr


# ---------------------------------------------------------------- sky
STOPS = [
    (0.00, (16, 13, 48)), (0.22, (44, 26, 84)), (0.42, (104, 42, 108)),
    (0.58, (172, 66, 106)), (0.70, (214, 100, 92)), (0.80, (238, 146, 88)),
    (0.90, (248, 190, 110)), (1.00, (250, 214, 142)),
]

hz = int(SH * HORIZON)
ys = np.linspace(0, 1, hz)
pos = np.array([s[0] for s in STOPS])
cols = np.array([s[1] for s in STOPS], dtype=float)
sky = np.stack([np.interp(ys, pos, cols[:, c]) for c in range(3)], axis=1)
col = np.repeat(sky[:, None, :], SW, axis=1)
img = Image.new("RGB", (SW, SH), (12, 10, 34))
img.paste(Image.fromarray(col.astype(np.uint8), "RGB"), (0, 0))

scx, scy, sr = SUN[0] * SW, SUN[1] * SH, S(SUN[2])

# sun glow: stacked translucent discs, widest first
glow = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for i in range(26):
    t = i / 25
    r = sr * (1 + 4.6 * (1 - t) ** 1.7)
    a = int(3 + 30 * t ** 2.4)
    c = (255, int(206 + 34 * t), int(150 + 70 * t), a)
    gd.ellipse([scx - r, scy - r, scx + r, scy + r], fill=c)
glow = glow.filter(ImageFilter.GaussianBlur(S(9)))
img = Image.alpha_composite(img.convert("RGBA"), glow)

# sun disc
d = ImageDraw.Draw(img, "RGBA")
d.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], fill=(255, 232, 186, 255))
d.ellipse([scx - sr * .82, scy - sr * .82, scx + sr * .82, scy + sr * .82],
          fill=(255, 246, 224, 255))

# ------------------------------------------------------- speed lines
rays = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
rd = ImageDraw.Draw(rays)
for i in range(64):
    a = random.uniform(0, math.tau)
    r0 = sr * random.uniform(1.25, 2.1)
    r1 = r0 + sr * random.uniform(0.9, 4.4)
    wdt = max(1, S(random.uniform(0.5, 2.3)))
    al = int(random.uniform(12, 46))
    rd.line([(scx + r0 * math.cos(a), scy + r0 * math.sin(a)),
             (scx + r1 * math.cos(a), scy + r1 * math.sin(a))],
            fill=(255, 226, 190, al), width=wdt)
rays = rays.filter(ImageFilter.GaussianBlur(S(1.4)))
img = Image.alpha_composite(img, rays)

# ---------------------------------------------------------- halftone
ht = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
hd = ImageDraw.Draw(ht)
step = S(13)
for gy in range(0, int(SH * 0.62), step):
    for gx in range(-step, SW + step, step):
        ox = (gy // step % 2) * step / 2
        t = 1 - gy / (SH * 0.62)
        r = step * 0.30 * t
        if r > 0.4:
            hd.ellipse([gx + ox - r, gy - r, gx + ox + r, gy + r],
                       fill=(255, 214, 236, int(26 * t)))
img = Image.alpha_composite(img, ht)

# ------------------------------------------------- gyroid lattice
# sin x cos y + sin y cos z + sin z cos x = 0, sliced at z -- the scaffold
N = 1200
span = 8.6 * math.pi
gx, gy = np.meshgrid(np.linspace(0, span, N), np.linspace(0, span, N))
gz = 0.62
f = (np.sin(gx) * np.cos(gy) + np.sin(gy) * np.cos(gz)
     + np.sin(gz) * np.cos(gx))
band = (np.abs(f) < 0.36).astype(np.uint8) * 255

lat = Image.fromarray(band, "L").resize((S(408), S(408)), Image.LANCZOS)
lat = lat.rotate(-13, resample=Image.BICUBIC, expand=False)
lw, lh = lat.size
lx, ly = int(scx - lw / 2 + S(6)), int(scy - lh / 2 - S(4))

# struts read as dark silhouette against the sun, with a lit cyan rim
edge = lat.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(S(1.1)))
strut = Image.new("RGBA", (lw, lh), (26, 16, 44, 236))
strut.putalpha(lat.point(lambda v: int(v * 0.92)))
rim = Image.new("RGBA", (lw, lh), CYAN + (255,))
rim.putalpha(edge.point(lambda v: min(255, int(v * 2.1))))
panel = Image.alpha_composite(strut, rim)

halo = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
halo.paste(panel, (lx, ly), panel)
halo = halo.filter(ImageFilter.GaussianBlur(S(7)))
img = Image.alpha_composite(img, Image.blend(
    Image.new("RGBA", (SW, SH), (0, 0, 0, 0)), halo, 0.55))
img.paste(panel, (lx, ly), panel)
d = ImageDraw.Draw(img, "RGBA")

# ------------------------------------------------------ mountains
def ridge(seed, amp, base, roughness=4):
    rng = random.Random(seed)
    phases = [(rng.uniform(0, math.tau), rng.uniform(0.6, 1.0)) for _ in range(roughness)]
    pts = []
    for x in range(0, SW + S(8), S(8)):
        u = x / SW
        y = base
        for k, (ph, w) in enumerate(phases, start=1):
            y -= amp * w * math.sin(u * math.pi * (k * 1.7) + ph) / k
        pts.append((x, y))
    return pts


LAYERS = [
    (11, S(74), SH * 0.716, (74, 44, 96)),
    (23, S(58), SH * 0.792, (48, 28, 70)),
    (37, S(40), SH * 0.846, (28, 17, 48)),
]
for seed, amp, base, colr in LAYERS:
    pts = ridge(seed, amp, base)
    d.polygon(pts + [(SW, SH), (0, SH)], fill=colr + (255,))

# foreground ridge
fg = ridge(53, S(26), SH * 0.922, roughness=3)
d.polygon(fg + [(SW, SH), (0, SH)], fill=(13, 9, 26, 255))


def ridge_y(pts, x):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / max(1e-6, x1 - x0)
            return y0 + (y1 - y0) * t
    return pts[-1][1]


# --------------------------------------------------- lone figure
fx = SW * 0.468
fy = ridge_y(fg, fx) + S(2)
INK = (9, 6, 20, 255)
u = S(1.4)
d.ellipse([fx - 5.6 * u, fy - 46 * u, fx + 5.6 * u, fy - 34.4 * u], fill=INK)
d.polygon([(fx - 1.6 * u, fy - 35.5 * u), (fx + 1.6 * u, fy - 35.5 * u),
           (fx + 2.0 * u, fy - 31 * u), (fx - 2.0 * u, fy - 31 * u)], fill=INK)
d.polygon([(fx - 6.6 * u, fy - 31.5 * u), (fx + 6.6 * u, fy - 31.5 * u),
           (fx + 5.0 * u, fy - 14 * u), (fx - 5.0 * u, fy - 14 * u)], fill=INK)
d.polygon([(fx + 5.4 * u, fy - 30 * u), (fx + 8.6 * u, fy - 22 * u),
           (fx + 7.0 * u, fy - 20.6 * u), (fx + 3.6 * u, fy - 27 * u)], fill=INK)
d.polygon([(fx - 5.0 * u, fy - 15 * u), (fx - 0.7 * u, fy - 15 * u),
           (fx - 1.3 * u, fy), (fx - 4.6 * u, fy)], fill=INK)
d.polygon([(fx + 0.7 * u, fy - 15 * u), (fx + 5.0 * u, fy - 15 * u),
           (fx + 4.8 * u, fy), (fx + 1.5 * u, fy)], fill=INK)

# ------------------------------------------------------- petals
pet = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
for _ in range(58):
    px = random.uniform(0, SW)
    py = random.uniform(0, SH * 0.80)
    ln = S(random.uniform(5.5, 11.5))
    wd = ln * random.uniform(0.46, 0.64)
    al = int(random.uniform(70, 190))
    tint = random.choice([(255, 208, 226), (255, 226, 236), (252, 190, 212)])
    p = Image.new("RGBA", (int(ln * 2), int(ln * 2)), (0, 0, 0, 0))
    pd = ImageDraw.Draw(p)
    pd.ellipse([ln - wd / 2, ln * 0.35, ln + wd / 2, ln * 1.65], fill=tint + (al,))
    pd.polygon([(ln - wd / 2, ln * 1.2), (ln + wd / 2, ln * 1.2), (ln, ln * 1.9)],
               fill=tint + (al,))
    p = p.rotate(random.uniform(0, 360), resample=Image.BICUBIC)
    pet.alpha_composite(p, (int(px), int(py)))
pet = pet.filter(ImageFilter.GaussianBlur(S(0.5)))
img = Image.alpha_composite(img, pet)

# ------------------------------------------- scrim behind the type
scrim = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
sd = ImageDraw.Draw(scrim)
for i in range(90):
    t = i / 89
    x1 = int(SW * 0.58 * (1 - t)) + 1
    sd.rectangle([0, 0, x1, SH], fill=(10, 7, 26, int(5 + 60 * (1 - t) ** 1.35)))
scrim = scrim.filter(ImageFilter.GaussianBlur(S(14)))
img = Image.alpha_composite(img, scrim)
d = ImageDraw.Draw(img, "RGBA")

# --------------------------------------------------------- type
f_eb = font(MENLO, S(11.5))
f_nm = font(FUTURA, S(64))
f_tg = font(AVENIR, S(21), index=7)
f_sb = font(MENLO, S(11))

x0 = S(64)
d.text((x0, S(300)), "", font=f_eb)
track(d, (x0, S(88)), EYEBROW, f_eb, AMBER + (232,), S(1.5))

shadow = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
ImageDraw.Draw(shadow).text((x0 + S(3), S(110) + S(3)), NAME, font=f_nm,
                            fill=(8, 5, 20, 150))
shadow = shadow.filter(ImageFilter.GaussianBlur(S(4)))
img = Image.alpha_composite(img, shadow)
d = ImageDraw.Draw(img, "RGBA")
d.text((x0, S(110)), NAME, font=f_nm, fill=BONE + (255,))

d.line([(x0, S(194)), (x0 + S(96), S(194))], fill=AMBER + (220,), width=max(1, S(2)))
d.text((x0, S(210)), TAGLINE, font=f_tg, fill=(238, 226, 232, 244))
track(d, (x0, S(248)), SUB, f_sb, MUTED + (208,), S(1.2))

# vertical Japanese, right edge
f_kj = font(HIRA_MIN, S(96), index=1)
f_vk = font(HIRA_GO, S(17), index=0)
kx = SW - S(96)
d.text((kx, S(92)), "骨", font=f_kj, fill=(255, 236, 214, 60))
vy = S(214)
for ch in "機械学習":
    w = d.textlength(ch, font=f_vk)
    d.text((kx + S(22) - w / 2, vy), ch, font=f_vk, fill=(255, 226, 200, 120))
    vy += S(21)

# grain
g = (np.random.default_rng(4).normal(0, 3.0, (SH // 3, SW // 3, 1))
     .repeat(3, axis=2))
gi = Image.fromarray(np.clip(g + 128, 0, 255).astype(np.uint8), "RGB").resize(
    (SW, SH), Image.BILINEAR)
img = Image.blend(img.convert("RGB"), Image.blend(img.convert("RGB"), gi, 1.0), 0.045)

out = img.resize((W, H), Image.LANCZOS)
# JPEG rather than PNG: palette-quantising a full-bleed sky gradient dithers it
# visibly, and lossless PNG costs ~410KB against ~169KB here at q94.
out.save("banner.jpg", quality=94, subsampling=0, optimize=True, progressive=True)
print(f"banner.jpg  {W}x{H}")
