"""Skill stamps for the profile README.

Hanko-style vermillion seals, one per skill, laid out as a single grid image.
Ink is deliberately uneven -- eroded edges and specks -- so it reads as pressed
ink rather than a vector circle. Opaque, so it sits correctly on GitHub's light
and dark themes alike.

    python3 build_stamps.py
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 4
S = lambda v: int(round(v * SS))

FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"
HIRA_GO = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"

VERMILLION = (196, 46, 38)
PAPER = (252, 249, 244)
# tone-on-tone: the gloss must read as ink texture, not as a second word.
# (alpha here would be wiped by the later putalpha, so it is a solid blend)
GLOSS = (208, 84, 74)

COLS, ROWS = 6, 2
DIA = 150
PITCH_X, PITCH_Y = 172, 178
PAD = 16

# (label lines, japanese gloss) -- the stack actually present in the repos
STAMPS = [
    (["PYTHON"], "蛇"),
    (["NUM", "PY"], "数"),
    (["PANDAS"], "表"),
    (["SCIKIT", "LEARN"], "学"),
    (["SCIPY"], "科"),
    (["MATPLOT", "LIB"], "図"),
    (["TYPE", "SCRIPT"], "型"),
    (["JAVA", "SCRIPT"], "動"),
    (["NODE", "JS"], "節"),
    (["EXPRESS"], "速"),
    (["FLUTTER"], "羽"),
    (["DART"], "矢"),
]


def font(path, px, index=0):
    try:
        return ImageFont.truetype(path, px, index=index)
    except Exception:
        return ImageFont.truetype(path, px)


def ink_mask(size, seed):
    """Disc alpha with eroded edges and a few dry-ink specks."""
    rng = np.random.default_rng(seed)
    n = size
    yy, xx = np.mgrid[0:n, 0:n]
    cx = cy = (n - 1) / 2
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (n / 2)

    noise = rng.normal(0, 1, (n // 6, n // 6))
    noise = np.array(Image.fromarray(
        ((noise - noise.min()) / np.ptp(noise) * 255).astype(np.uint8)
    ).resize((n, n), Image.BICUBIC), dtype=float) / 255.0

    a = np.clip((0.985 - r) * 26, 0, 1)          # hard disc, soft rim
    a *= np.clip(0.55 + 0.95 * noise, 0, 1)      # uneven ink load
    a[r > 0.93] *= np.clip(noise[r > 0.93] * 2.1, 0, 1)  # ragged edge
    a[(noise < 0.10) & (r < 0.9)] *= 0.25        # dry specks
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "L")


def stamp(lines, gloss, seed):
    d_px = S(DIA)
    canvas = int(d_px * 1.28)
    img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    o = (canvas - d_px) // 2
    dr.ellipse([o, o, o + d_px, o + d_px], fill=VERMILLION + (255,))

    # inner hairline ring, knocked out
    ring = S(7)
    dr.ellipse([o + ring, o + ring, o + d_px - ring, o + d_px - ring],
               outline=PAPER + (255,), width=max(1, S(1.6)))

    # japanese gloss, faint, behind the latin text
    fg = font(HIRA_GO, S(66))
    gw = dr.textlength(gloss, font=fg)
    bb = fg.getbbox(gloss)
    dr.text((canvas / 2 - gw / 2, canvas / 2 - (bb[3] + bb[1]) / 2),
            gloss, font=fg, fill=GLOSS + (255,))

    # latin lines, fitted
    limit = d_px * 0.66
    size = S(30)
    while size > S(9):
        f = font(FUTURA, size, index=0)
        if max(dr.textlength(l, font=f) for l in lines) <= limit:
            break
        size -= S(0.7)
    f = font(FUTURA, size, index=0)
    lh = size * 1.06
    total = lh * len(lines)
    y = canvas / 2 - total / 2 - S(1)
    for line in lines:
        w = dr.textlength(line, font=f)
        dr.text((canvas / 2 - w / 2, y), line, font=f, fill=PAPER + (255,))
        y += lh

    # press the ink
    alpha = img.getchannel("A")
    mask = ink_mask(canvas, seed).resize((canvas, canvas))
    img.putalpha(Image.fromarray(
        (np.array(alpha, float) * np.array(mask, float) / 255).astype(np.uint8), "L"))
    return img.rotate(random.Random(seed).uniform(-5, 5),
                      resample=Image.BICUBIC, expand=False)


W = PAD * 2 + PITCH_X * COLS
Hh = PAD * 2 + PITCH_Y * ROWS - (PITCH_Y - DIA) + 6
sheet = Image.new("RGBA", (S(W), S(Hh)), (0, 0, 0, 0))

for i, (lines, gloss) in enumerate(STAMPS):
    r, c = divmod(i, COLS)
    st = stamp(lines, gloss, seed=101 + i * 7)
    cx = S(PAD + PITCH_X * c + PITCH_X / 2)
    cy = S(PAD + PITCH_Y * r + DIA / 2)
    sheet.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))

out = sheet.resize((W, Hh), Image.LANCZOS)
out.save("stamps.png", optimize=True)
print(f"stamps.png  {W}x{Hh}  ({len(STAMPS)} stamps)")
