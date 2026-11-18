#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news poster (1024x1024 PNG).

A single broadsheet page, "THE WORLD IN ONE DAY", summing up Wednesday
18 November 2026. Every fact was re-verified in this build session against
reporting published on 18 November 2026 (Reuters, AP via AAP, RNZ, Fiji
Meteorological Service, Cook Islands Meteorological Service, Malaysiakini,
Xinhua). No figure is invented and no story comes from another day.

Layout: navy header band; full-width lead story with a drawn Gulf map;
five stories plus a numbers box in a 2 x 3 grid; an ALSO strip; a sources
footer. Deterministic: no timestamps, no randomness, fixed fonts.
Run: python3 draw_poster.py  ->  entry.png
"""

import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 243, 234)
NAVY = (16, 32, 54)
NAVY_LIGHT = (28, 52, 84)
GOLD = (198, 154, 52)
GOLD_LIGHT = (238, 214, 140)
INK = (22, 22, 22)
GREY = (88, 92, 98)
CARD = (255, 255, 255)
LINE = (205, 198, 182)
RED = (158, 28, 28)
TEAL = (13, 92, 102)
GREEN = (28, 92, 48)
BLUE = (30, 58, 95)
SLATE = (71, 85, 105)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def fnt(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, font, fill, max_w, leading):
    for line in wrap(d, text, font, max_w):
        d.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def star(d, cx, cy, outer, inner, points, fill, outline):
    pts = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline, width=2)


def halo_text(d, x, y, text, font, fill=(255, 255, 255)):
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((x + dx, y + dy), text, font=font, fill=(8, 24, 36))
    d.text((x, y), text, font=font, fill=fill)


# ------------------------------------------------------------------ content
LEAD_HEAD = "IRAN'S DRONES HIT A US BASE IN KUWAIT"
LEAD_BODY = (
    "Iran widened its Gulf attacks on Wednesday, sending drones at the "
    "US Ali Al Salem air base in Kuwait \u2014 its first strike there since "
    "September \u2014 and at targets in Bahrain, a day after US jets hit "
    "Qeshm Island."
)
LEAD_NOTE = "Kuwait's defences engaged the drones; Bahrain said it stopped several attacks."

CELLS = [
    {
        "tag": "UNITED STATES",
        "color": BLUE,
        "head": "PELTOLA WINS ALASKA \u2014 DEMOCRATS TO 56",
        "body": (
            "Mary Peltola beats Republican Dan Sullivan for Alaska's Senate "
            "seat \u2014 the Democrats' ninth flip of the midterms and a 56\u201344 majority."
        ),
    },
    {
        "tag": "PACIFIC",
        "color": TEAL,
        "head": "CYCLONE XAVIER, CATEGORY 5, BEARS DOWN",
        "body": (
            "Severe Tropical Cyclone Xavier reaches the Northern Cook Islands "
            "with sustained winds of 220 km/h and gusts up to 315 km/h. "
            "Shelters open on the atolls."
        ),
    },
    {
        "tag": "MARKETS",
        "color": GREEN,
        "head": "ALSTOM SINKS TO A 21-YEAR LOW",
        "body": (
            "The French train maker's shares fall 9% to \u20ac9.08, their lowest "
            "since May 2005, after net debt more than doubled to \u20ac1.1bn."
        ),
    },
    {
        "tag": "GAZA",
        "color": RED,
        "head": "\u201cANOTHER WINTER IN TENTS AND RUBBLE\u201d",
        "body": (
            "The Board of Peace tells the UN Security Council the Gaza "
            "ceasefire could collapse without urgent action; it urges "
            "winter shelter aid now."
        ),
    },
    {
        "tag": "EARTHQUAKE",
        "color": SLATE,
        "head": "MAGNITUDE 6.0 QUAKE IN PAPUA NEW GUINEA",
        "body": (
            "A magnitude 6.0 earthquake strikes Papua New Guinea at a depth "
            "of 10 km, the German Research Centre for Geosciences says."
        ),
    },
]

NUMBERS = [
    "Brent $91.69  \u25bc 1.6%    WTI $84.06  \u25bc 2.3%",
    "US Senate: Democrats 56 \u2014 Republicans 44",
    "Xavier: 220 km/h sustained, gusts 315 km/h",
    "Alstom \u2212 9% to \u20ac9.08 \u00b7 \u2212 64% in 2026",
]

ALSO = (
    "ALSO:  Malaysia to review leaked Deutsche Bank 1MDB files  \u00b7  "
    "Xi opens APEC in Shenzhen  \u00b7  Most Gulf bourses fall"
)
FOOTER = (
    "Sources: Reuters  \u00b7  AP  \u00b7  AAP  \u00b7  RNZ  \u00b7  Fiji Meteorological Service  \u00b7  "
    "Cook Islands Meteorological Service  \u00b7  Malaysiakini  \u00b7  Xinhua"
)
FOOTER2 = "All events happened, or were first reported, on Wednesday 18 November 2026."


# ------------------------------------------------------------------ map
def draw_gulf(d, x0, y0, x1, y1):
    """Stylised Gulf map: blue sea, sand land, three marked places."""
    sea = (24, 74, 96)
    sand = (226, 208, 164)
    sand_dark = (206, 184, 134)
    d.rectangle([x0, y0, x1, y1], fill=sea)
    # Iran, top edge
    d.polygon(
        [(x0, y0), (x1, y0), (x1, y0 + 96), (x1 - 88, y0 + 88),
         (x1 - 170, y0 + 52), (x0 + 128, y0 + 44), (x0 + 64, y0 + 20)],
        fill=sand_dark,
    )
    # Arabia, bottom edge
    d.polygon(
        [(x0, y0 + 196), (x0 + 96, y0 + 168), (x0 + 190, y0 + 188),
         (x0 + 252, y0 + 226), (x1, y0 + 252), (x1, y1), (x0, y1)],
        fill=sand,
    )
    # the Gulf water between them
    d.polygon(
        [(x0 + 64, y0 + 20), (x0 + 128, y0 + 44), (x1 - 170, y0 + 52),
         (x1 - 88, y0 + 88), (x1, y0 + 96), (x1, y0 + 252),
         (x0 + 252, y0 + 226), (x0 + 190, y0 + 188), (x0 + 96, y0 + 168),
         (x0, y0 + 196), (x0, y0 + 120)],
        fill=(58, 122, 152),
    )
    for xx, yy in ((x0 + 60, y0 + 110), (x0 + 200, y0 + 150), (x0 + 120, y0 + 210)):
        d.arc([xx - 13, yy - 5, xx + 13, yy + 5], 200, 340,
              fill=(150, 190, 210), width=2)
    # Qeshm Island: US strike on Tuesday
    qx, qy = x0 + 268, y0 + 58
    d.ellipse([qx - 6, qy - 6, qx + 6, qy + 6], fill=(255, 255, 255),
              outline=(10, 30, 40), width=2)
    halo_text(d, qx - 118, qy - 24, "QESHM ISLAND", fnt(BOLD, 13))
    d.text((qx - 118, qy + 8), "US strike Tue", font=fnt(REG, 12), fill=(255, 255, 255))
    # Ali Al Salem, Kuwait: gold starburst
    kx, ky = x0 + 96, y0 + 148
    star(d, kx, ky, 30, 12, 12, (245, 158, 11), (234, 88, 12))
    star(d, kx, ky, 13, 6, 8, (254, 240, 138), (234, 88, 12))
    halo_text(d, kx - 26, ky + 36, "KUWAIT", fnt(BOLD, 14))
    d.text((kx - 26, ky + 54), "Ali Al Salem", font=fnt(REG, 12), fill=(255, 255, 255))
    # Bahrain: orange dot
    bx, by = x0 + 218, y0 + 196
    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(234, 88, 12),
              outline=(255, 255, 255), width=2)
    halo_text(d, bx + 12, by - 8, "BAHRAIN", fnt(BOLD, 13))
    d.text((bx + 12, by + 10), "intercepted", font=fnt(REG, 12), fill=(255, 255, 255))
    # strait label
    halo_text(d, x0 + 238, y0 + 118, "STRAIT OF", fnt(BOLD, 11))
    halo_text(d, x0 + 238, y0 + 132, "HORMUZ", fnt(BOLD, 11))


# ------------------------------------------------------------------ page
def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # header band
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 118, W, 122], fill=GOLD)
    d.text((32, 18), "THE WORLD IN ONE DAY", font=fnt(BOLD, 52), fill=(255, 255, 255))
    d.text((32, 80), "WEDNESDAY  18  NOVEMBER  2026", font=fnt(BOLD, 24), fill=GOLD_LIGHT)
    d.text((742, 84), "WORLD NEWS", font=fnt(BOLD, 20), fill=(170, 190, 215))
    d.text((742, 22), "ONE DAY,", font=fnt(BOLD, 20), fill=(255, 255, 255))
    d.text((742, 46), "ONE IMAGE.", font=fnt(BOLD, 20), fill=(255, 255, 255))

    # lead card
    d.rectangle([28, 140, 996, 428], fill=CARD, outline=LINE, width=2)
    d.rectangle([28, 140, 996, 146], fill=RED)
    d.text((48, 158), "LEAD STORY  \u00b7  THE GULF", font=fnt(BOLD, 19), fill=RED)
    block(d, 48, 190, LEAD_HEAD, fnt(BOLD, 38), INK, 500, 46)
    block(d, 48, 292, LEAD_BODY, fnt(REG, 18), INK, 510, 23)
    d.text((48, 410), LEAD_NOTE, font=fnt(REG, 16), fill=GREY)
    draw_gulf(d, 580, 158, 976, 410)

    # grid: 2 columns x 3 rows, five stories + numbers box
    gx0, gy0 = 28, 446
    cw, ch, gap = 472, 148, 18
    for i, cell in enumerate(CELLS):
        x = gx0 + (i % 2) * (cw + gap)
        y = gy0 + (i // 2) * (ch + gap)
        d.rectangle([x, y, x + cw, y + ch], fill=CARD, outline=LINE, width=2)
        d.rectangle([x, y, x + cw, y + 6], fill=cell["color"])
        d.text((x + 16, y + 14), cell["tag"], font=fnt(BOLD, 15), fill=cell["color"])
        block(d, x + 16, y + 38, cell["head"], fnt(BOLD, 20), INK, cw - 32, 24)
        block(d, x + 16, y + 88, cell["body"], fnt(REG, 15), INK, cw - 32, 19)
    # numbers box, last cell
    x = gx0 + cw + gap
    y = gy0 + 2 * (ch + gap)
    d.rectangle([x, y, x + cw, y + ch], fill=NAVY, outline=NAVY, width=2)
    d.text((x + 16, y + 14), "BY THE NUMBERS", font=fnt(BOLD, 17), fill=GOLD_LIGHT)
    yy = y + 44
    for line in NUMBERS:
        d.text((x + 16, yy), line, font=fnt(REG, 17), fill=(255, 255, 255))
        yy += 25

    # also strip
    d.rectangle([28, 934, 996, 970], fill=(243, 233, 210), outline=LINE, width=1)
    block(d, 44, 944, ALSO, fnt(BOLD, 14), (60, 48, 20), 936, 18)

    # footer
    d.text((32, 982), FOOTER, font=fnt(REG, 13), fill=(107, 114, 128))
    d.text((32, 1000), FOOTER2, font=fnt(REG, 13), fill=(107, 114, 128))
    return img


if __name__ == "__main__":
    poster = draw()
    poster.save("entry.png", format="PNG", optimize=False)
    print("wrote entry.png", poster.size)
